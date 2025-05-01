use bevy::{
    prelude::*,
    render::{
        camera::ClearColor,
        extract_resource::{ExtractResource, ExtractResourcePlugin},
        render_asset::RenderAssets,
        render_graph::{GraphInput, Node, RenderGraph, RenderLabel},
        render_resource::{
            AsBindGroup, AsBindGroupError, BindGroup, BindGroupLayout, BindGroupLayoutEntry,
            BindingType, BlendState, CachedComputePipelineId, CachedRenderPipelineId,
            ColorTargetState, ColorWrites, ComputePassDescriptor, ComputePipelineDescriptor,
            FragmentState, FrontFace, LoadOp, MultisampleState, Operations, PipelineCache,
            PolygonMode, PrimitiveState, PrimitiveTopology,
            RenderPassColorAttachment, RenderPassDescriptor, RenderPipelineDescriptor,
            ShaderStages, ShaderType, StoreOp, TextureFormat, VertexState,
        },
        renderer::RenderDevice,
        settings::{Backends, RenderCreation, WgpuSettings},
        storage::{GpuShaderStorageBuffer, ShaderStorageBuffer},
        texture::{FallbackImage, GpuImage},
        view::ViewTarget,
        Render, RenderApp, RenderPlugin, RenderSet,
    },
    DefaultPlugins,
};

use rand::prelude::*;
use std::borrow::Cow;

const PARTICLE_COUNT: usize = 100_000;
const SHADER_PATH_COMPUTE: &str = "compute.wgsl";
const SHADER_PATH_VERTEX: &str = "render.wgsl";

#[repr(C)]
#[derive(Debug, Clone, Copy, bytemuck::Pod, bytemuck::Zeroable, ShaderType)]
struct VertexData {
    pos: [f32; 2],
    vel: [f32; 2],
}

#[repr(C)]
#[derive(Debug, Clone, Copy, bytemuck::Pod, bytemuck::Zeroable, ShaderType)]
struct PushConstants {
    attr: [f32; 2],
    attr_strength: f32,
    delta_t: f32,
    _pad: [f32; 4]
}

fn main() {
    let render_plugin = RenderPlugin {
        render_creation: RenderCreation::Automatic(WgpuSettings {
            backends: Some(Backends::VULKAN),
            ..default()
        }),
        ..default()
    };
    let mut app = App::new();
    app.insert_resource(ClearColor(Color::BLACK));
    app.add_plugins((DefaultPlugins.set(render_plugin), ComputePlugin));
    app.add_plugins(ExtractResourcePlugin::<ComputeBuffers>::default());
    app.add_systems(Startup, setup);
    app.run();
}

fn setup(mut commands: Commands, mut buff: ResMut<Assets<ShaderStorageBuffer>>) {
    // Generate random particle data
    let input_data: Vec<VertexData> = (0..PARTICLE_COUNT)
        .map(|_| VertexData {
            pos: [
                rand::random::<f32>() * 2.0 - 1.0, // x
                rand::random::<f32>() * 2.0 - 1.0, // y
            ],
            vel: [0.0, 0.0], // velocity x, y
        })
        .collect();

    // Initialize uniform
    let uniform = PushConstants {
        attr: [0.0, 0.0],
        attr_strength: 1.0,
        delta_t: 0.0,
        _pad: [0.0,0.0,0.0,0.0]
    };

    commands.insert_resource(ComputeBuffers {
        vertices: buff.add(input_data),
        push: uniform,
    });

    // Spawn camera
    commands.spawn(Camera2d::default());
}

#[derive(RenderLabel, Clone, Hash, Debug, PartialEq, Eq)]
pub struct ComputeNode;

pub struct ComputePlugin;

impl Plugin for ComputePlugin {
    fn build(&self, app: &mut App) {
        app.add_systems(Update, update_uniform);
    }

    fn finish(&self, app: &mut App) {
        if let Some(app) = app.get_sub_app_mut(RenderApp) {
            app.init_resource::<ComputePipeline>();
            app.init_resource::<RenderPipeline>();
            app.add_systems(
                Render,
                (
                    prepare_buffers.in_set(RenderSet::Prepare),
                    prepare_render_pipeline.in_set(RenderSet::Prepare),
                ),
            );

            let mut render_graph = app.world_mut().get_resource_mut::<RenderGraph>().unwrap();
            render_graph.add_node(ComputeNode, DispatchCompute {});
            render_graph.add_node(RenderNodeLabel, RenderNode::default());

            let r = render_graph.try_add_node_edge(GraphInput, ComputeNode);
            if r.is_err() {
                println!("{:?}", r);
            }
            let r = render_graph.try_add_node_edge(ComputeNode, RenderNodeLabel);
            if r.is_err() {
                println!("{:?}", r);
            }
        }
    }
}

fn update_uniform(
    time: Res<Time>,
    mut compute: ResMut<ComputeBuffers>,
) {
    compute.push.delta_t = time.delta_secs() as f32;
}

#[derive(Resource, AsBindGroup, Debug, Clone, ExtractResource)]
struct ComputeBuffers {
    #[storage(0, visibility(compute))]
    vertices: Handle<ShaderStorageBuffer>,
    #[uniform(1, visibility(compute))]
    push: PushConstants,
}

#[derive(Resource)]
struct ComputeBindGroup(pub BindGroup);

fn prepare_buffers(
    mut commands: Commands,
    pipeline: Res<ComputePipeline>,
    buffers: Res<ComputeBuffers>,
    render_device: Res<RenderDevice>,
    render_assets_images: Res<RenderAssets<GpuImage>>,
    fallback_image: Res<FallbackImage>,
    render_assets_buffers: Res<RenderAssets<GpuShaderStorageBuffer>>,
) {
    let mut param = (render_assets_images, fallback_image, render_assets_buffers);
    let result = buffers.as_bind_group(&pipeline.bind_group_layout, &render_device, &mut param);
    match result {
        Ok(buffers) => {
            commands.insert_resource(ComputeBindGroup(buffers.bind_group));
        }
        Err(AsBindGroupError::RetryNextUpdate) => {
            println!("retry next update");
        }
        Err(e) => {
            panic!("{}", e);
        }
    }
}

#[derive(Resource)]
struct ComputePipeline {
    bind_group_layout: BindGroupLayout,
    compute_pipeline: CachedComputePipelineId,
}

impl FromWorld for ComputePipeline {
    fn from_world(world: &mut World) -> Self {
        let render_device = world.resource::<RenderDevice>();
        let bind_group_layout = render_device.create_bind_group_layout(
            "ComputeBuffers",
            &vec![
                // Vertices buffer
                BindGroupLayoutEntry {
                    binding: 0,
                    visibility: ShaderStages::COMPUTE,
                    ty: BindingType::Buffer {
                        ty: bevy::render::render_resource::BufferBindingType::Storage {
                            read_only: false,
                        },
                        has_dynamic_offset: false,
                        min_binding_size: None,
                    },
                    count: None,
                },
                // Uniform buffer
                BindGroupLayoutEntry {
                    binding: 1,
                    visibility: ShaderStages::COMPUTE,
                    ty: BindingType::Buffer {
                        ty: bevy::render::render_resource::BufferBindingType::Uniform,
                        has_dynamic_offset: false,
                        min_binding_size: None,
                    },
                    count: None,
                },
            ],
        );

        let shader = world.load_asset(SHADER_PATH_COMPUTE);
        let pipeline_cache = world.resource::<PipelineCache>();

        let compute_pipeline = pipeline_cache.queue_compute_pipeline(ComputePipelineDescriptor {
            label: None,
            layout: vec![bind_group_layout.clone()],
            push_constant_ranges: Vec::new(),
            shader: shader.clone(),
            shader_defs: vec![],
            entry_point: Cow::from("main"),
            zero_initialize_workgroup_memory: false,
        });

        ComputePipeline {
            bind_group_layout,
            compute_pipeline,
        }
    }
}

struct DispatchCompute;

impl Node for DispatchCompute {
    fn run(
        &self,
        _graph: &mut bevy::render::render_graph::RenderGraphContext,
        render_context: &mut bevy::render::renderer::RenderContext,
        world: &bevy::prelude::World,
    ) -> Result<(), bevy::render::render_graph::NodeRunError> {
        let kernel_pipeline = world.get_resource::<ComputePipeline>();
        let kernel_bind_group = world.get_resource::<ComputeBindGroup>();
        let pipeline_cache = world.resource::<PipelineCache>();

        if let (Some(kernel_pipeline), Some(kernel_bind_group)) =
            (kernel_pipeline, kernel_bind_group)
        {
            let mut pass =
                render_context
                    .command_encoder()
                    .begin_compute_pass(&ComputePassDescriptor {
                        label: Some("Compute Pass"),
                        ..Default::default()
                    });
            if let Some(real_pipeline) =
                pipeline_cache.get_compute_pipeline(kernel_pipeline.compute_pipeline)
            {
                pass.set_pipeline(&real_pipeline);
                pass.set_bind_group(0, &kernel_bind_group.0, &[]);
                pass.dispatch_workgroups(PARTICLE_COUNT as u32 / 256, 1, 1);
            }
        }
        Ok(())
    }
}

#[derive(Resource)]
struct RenderPipeline {
    pipeline: CachedRenderPipelineId,
    bind_group_layout: BindGroupLayout,
}

impl FromWorld for RenderPipeline {
    fn from_world(world: &mut World) -> Self {
        let render_device = world.resource::<RenderDevice>();
        let bind_group_layout = render_device.create_bind_group_layout(
            "RenderBuffers",
            &[BindGroupLayoutEntry {
                binding: 0,
                visibility: ShaderStages::VERTEX,
                ty: BindingType::Buffer {
                    ty: bevy::render::render_resource::BufferBindingType::Storage {
                        read_only: true,
                    },
                    has_dynamic_offset: false,
                    min_binding_size: None,
                },
                count: None,
            }],
        );

        let shader = world.load_asset(SHADER_PATH_VERTEX);
        let pipeline_cache = world.resource::<PipelineCache>();

        let pipeline = pipeline_cache.queue_render_pipeline(RenderPipelineDescriptor {
            label: None,
            layout: vec![bind_group_layout.clone()],
            vertex: VertexState {
                shader: shader.clone(),
                entry_point: "vs_main".into(),
                shader_defs: vec![],
                buffers: vec![],
            },
            fragment: Some(FragmentState {
                shader: shader,
                entry_point: "fs_main".into(),
                shader_defs: vec![],
                targets: vec![Some(ColorTargetState {
                    format: TextureFormat::Bgra8UnormSrgb,
                    blend: Some(BlendState::ALPHA_BLENDING),
                    write_mask: ColorWrites::ALL,
                })],
            }),
            primitive: PrimitiveState {
                topology: PrimitiveTopology::PointList,
                strip_index_format: None,
                front_face: FrontFace::Ccw,
                cull_mode: None,
                unclipped_depth: false,
                polygon_mode: PolygonMode::Fill,
                conservative: false,
            },
            depth_stencil: None,
            multisample: MultisampleState {
                count: 1,
                mask: !0,
                alpha_to_coverage_enabled: false,
            },
            push_constant_ranges: vec![],
            zero_initialize_workgroup_memory: false,
        });

        RenderPipeline {
            pipeline,
            bind_group_layout,
        }
    }
}

#[derive(Resource)]
struct RenderBindGroup(pub BindGroup);

fn prepare_render_pipeline(
    mut commands: Commands,
    pipeline: Res<RenderPipeline>,
    buffers: Res<ComputeBuffers>,
    render_device: Res<RenderDevice>,
    render_assets_images: Res<RenderAssets<GpuImage>>,
    fallback_image: Res<FallbackImage>,
    render_assets_buffers: Res<RenderAssets<GpuShaderStorageBuffer>>,
) {
    let mut param = (render_assets_images, fallback_image, render_assets_buffers);
    let result = buffers.as_bind_group(&pipeline.bind_group_layout, &render_device, &mut param);
    match result {
        Ok(buffers) => {
            commands.insert_resource(RenderBindGroup(buffers.bind_group));
        }
        Err(AsBindGroupError::RetryNextUpdate) => {
            println!("retry next update");
        }
        Err(e) => {
            panic!("{}", e);
        }
    }
}

#[derive(RenderLabel, Clone, Hash, Debug, PartialEq, Eq)]
struct RenderNodeLabel;

#[derive(Clone, Hash, Debug, PartialEq, Eq)]
pub struct RenderNode {
    view_target_id: Option<Entity>,
}

impl Node for RenderNode {
    fn update(&mut self, world: &mut World) {
        if let Ok((entity, _)) = world.query::<(Entity, &ViewTarget)>().get_single(world) {
            self.view_target_id = Some(entity);
        }
    }

    fn run(
        &self,
        _graph: &mut bevy::render::render_graph::RenderGraphContext,
        render_context: &mut bevy::render::renderer::RenderContext,
        world: &bevy::prelude::World,
    ) -> Result<(), bevy::render::render_graph::NodeRunError> {
        let pipeline_cache = world.resource::<PipelineCache>();
        let render_pipeline = world.resource::<RenderPipeline>();
        let render_bind_group = world.resource::<RenderBindGroup>();

        if let (Some(pipeline), Some(entity)) = (
            pipeline_cache.get_render_pipeline(render_pipeline.pipeline),
            self.view_target_id,
        ) {
            if let Some(view) = world.entity(entity).get::<ViewTarget>() {
                let mut render_pass =
                    render_context.begin_tracked_render_pass(RenderPassDescriptor {
                        label: Some("Particle Render Pass"),
                        color_attachments: &[Some(RenderPassColorAttachment {
                            view: &view.main_texture_view(),
                            resolve_target: None,
                            ops: Operations {
                                load: LoadOp::Load,
                                store: StoreOp::Store,
                            },
                        })],
                        depth_stencil_attachment: None,
                        occlusion_query_set: None,
                        timestamp_writes: None,
                    });

                render_pass.set_render_pipeline(pipeline);
                render_pass.set_bind_group(0, &render_bind_group.0, &[]);
                render_pass.draw(0..PARTICLE_COUNT as u32, 0..1);
            }
        }

        Ok(())
    }
}

impl Default for RenderNode {
    fn default() -> Self {
        Self {
            view_target_id: None,
        }
    }
}
