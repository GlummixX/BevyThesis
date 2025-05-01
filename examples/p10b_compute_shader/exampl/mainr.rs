mod utils;
mod vulkano;

use crate::utils::fps_counter::FpsCounter;
use crate::utils::shaders::{cs, fs, vs};
use crate::utils::vertex::Vertex;
use crate::vulkano::buffers::command_buffer::build_command_buffer;
use crate::vulkano::buffers::frame_buffer::create_frame_buffers;
use crate::vulkano::buffers::vertex_buffer::create_vertex_buffer;
use crate::vulkano::core::instance::{create_instance, load_vulkan_library};
use crate::vulkano::core::surface::build_surface;
use crate::vulkano::core::windows::{create_window, is_window_minimized};
use crate::vulkano::devices::logical_device::create_logical_device;
use crate::vulkano::devices::physical_device::{get_device_extension, select_physical_device};
use crate::vulkano::graphics_pipeline::compute_pipeline::create_compute_pipeline;
use crate::vulkano::graphics_pipeline::graphics_pipeline::create_graphics_pipeline;
use crate::vulkano::graphics_pipeline::render_pass::create_render_pass;
use crate::vulkano::graphics_pipeline::swap_chain::{create_swap_chain, recreate_swap_chain};
use ::vulkano::buffer::Subbuffer;
use ::vulkano::command_buffer::allocator::StandardCommandBufferAllocator;
use ::vulkano::command_buffer::{AutoCommandBufferBuilder, CommandBufferExecFuture, CommandBufferUsage, PrimaryAutoCommandBuffer};
use ::vulkano::descriptor_set::allocator::{StandardDescriptorSetAlloc, StandardDescriptorSetAllocator};
use ::vulkano::descriptor_set::layout::DescriptorSetLayout;
use ::vulkano::descriptor_set::{PersistentDescriptorSet, WriteDescriptorSet};
use ::vulkano::device::physical::PhysicalDevice;
use ::vulkano::device::{Device, DeviceExtensions, Queue};
use ::vulkano::image::Image;
use ::vulkano::instance::Instance;
use ::vulkano::memory::allocator::StandardMemoryAllocator;
use ::vulkano::pipeline::graphics::viewport::Viewport;
use ::vulkano::pipeline::{ComputePipeline, GraphicsPipeline, Pipeline};
use ::vulkano::render_pass::{Framebuffer, RenderPass};
use ::vulkano::shader::EntryPoint;
use ::vulkano::swapchain::{acquire_next_image, PresentFuture, Surface, Swapchain, SwapchainAcquireFuture, SwapchainPresentInfo};
use ::vulkano::sync::future::{FenceSignalFuture, JoinFuture};
use ::vulkano::sync::GpuFuture;
use ::vulkano::{sync, Validated, VulkanError, VulkanLibrary};
use std::sync::Arc;
use std::time::{Duration, SystemTime};
use winit::dpi::PhysicalSize;
use winit::event::{Event, WindowEvent};
use winit::event_loop::{ControlFlow, EventLoop};
use winit::window::Window;
use crate::utils::shaders::cs::PushConstants;

type VulkanFuture =
    Result<FenceSignalFuture<PresentFuture<CommandBufferExecFuture<JoinFuture<Box<dyn GpuFuture>, SwapchainAcquireFuture>>>>, Validated<VulkanError>>;

const PARTICLE_COUNT: usize = 1_000_000;
fn main() {
    let event_loop: EventLoop<()> = EventLoop::new();
    let library: Arc<VulkanLibrary> = load_vulkan_library();
    let instance: Arc<Instance> = create_instance(library, &event_loop, "Compute shader example");

    let window: Arc<Window> = create_window(&event_loop);
    let surface: Arc<Surface> = build_surface(&instance, &window);

    let device_extensions: DeviceExtensions = get_device_extension();
    let (physical_device, queue_family_index): (Arc<PhysicalDevice>, u32) = select_physical_device(&instance, &surface, &device_extensions);

    println!(
        "Using device: {} (type: {:?})",
        physical_device.properties().device_name,
        physical_device.properties().device_type
    );

    let (logical_device, mut queues): (Arc<Device>, _) = create_logical_device(physical_device, device_extensions, queue_family_index);
    let queue: Arc<Queue> = queues.next().unwrap();

    let vertex_shader: EntryPoint = vs::load(logical_device.clone()).unwrap().entry_point("main").unwrap();
    let fragment_shader: EntryPoint = fs::load(logical_device.clone()).unwrap().entry_point("main").unwrap();
    let compute_shader: EntryPoint = cs::load(logical_device.clone()).unwrap().entry_point("main").unwrap();

    let mut viewport: Viewport = Viewport {
        offset: [0.0, 0.0],
        extent: [0.0, 0.0],
        depth_range: 0.0..=1.0,
    };

    let (mut swap_chain, images): (Arc<Swapchain>, Vec<Arc<Image>>) = create_swap_chain(&logical_device, &surface);
    let render_pass: Arc<RenderPass> = create_render_pass(&logical_device, &swap_chain);

    let memory_allocator: Arc<StandardMemoryAllocator> = Arc::new(StandardMemoryAllocator::new_default(logical_device.clone()));
    let descriptor_set_allocator: StandardDescriptorSetAllocator = StandardDescriptorSetAllocator::new(logical_device.clone(), Default::default());
    let command_buffer_allocator: StandardCommandBufferAllocator = StandardCommandBufferAllocator::new(logical_device.clone(), Default::default());

    let vertex_buffer: Subbuffer<[Vertex]> = create_vertex_buffer(
        &memory_allocator,
        &command_buffer_allocator,
        &queue,
        PARTICLE_COUNT,
    );
    let mut frame_buffer: Vec<Arc<Framebuffer>> = create_frame_buffers(&memory_allocator, &render_pass, &images, &mut viewport);

    let compute_pipeline: Arc<ComputePipeline> = create_compute_pipeline(&logical_device, &compute_shader);
    let compute_descriptor_set: Arc<PersistentDescriptorSet<StandardDescriptorSetAlloc>> =
        create_compute_descriptor_set(&descriptor_set_allocator, &vertex_buffer, &compute_pipeline);

    let graphics_pipeline: Arc<GraphicsPipeline> = create_graphics_pipeline(
        &logical_device,
        &render_pass,
        &vertex_shader,
        &fragment_shader,
    );

    let mut recreate_swapchain: bool = false;
    let mut fps_counter: FpsCounter = FpsCounter::new(Duration::new(1, 0), &window);

    let start_time: SystemTime = SystemTime::now();
    let mut last_frame_time: SystemTime = start_time;
    let mut previous_frame_end: Option<Box<dyn GpuFuture>> = Some(sync::now(logical_device.clone()).boxed());
    event_loop.run(
        move |event: Event<()>, _, control_flow: &mut ControlFlow| match event {
            Event::WindowEvent {
                event: WindowEvent::CloseRequested,
                ..
            } => {
                *control_flow = ControlFlow::Exit;
            }

            Event::WindowEvent {
                event: WindowEvent::Resized(_),
                ..
            } => {
                recreate_swapchain = true;
            }

            Event::RedrawEventsCleared => {
                let dimensions: PhysicalSize<u32> = window.inner_size();
                if is_window_minimized(dimensions) {
                    return;
                }

                previous_frame_end.as_mut().unwrap().cleanup_finished();
                if recreate_swapchain {
                    let (new_swap_chain, new_images): (Arc<Swapchain>, Vec<Arc<Image>>) = recreate_swap_chain(&swap_chain, dimensions);
                    swap_chain = new_swap_chain;

                    frame_buffer = create_frame_buffers(&memory_allocator, &render_pass, &new_images, &mut viewport);
                    recreate_swapchain = false;
                };

                let now = SystemTime::now();
                let time = now.duration_since(start_time).unwrap().as_secs_f32();
                let delta_time = now.duration_since(last_frame_time).unwrap().as_secs_f32();
                last_frame_time = now;

                let push_constants: PushConstants = PushConstants {
                    attractor: [
                        0.8 * (2.8 * time).sin(),
                        0.5 * (0.8 * time).cos(),
                    ],
                    attractor_strength: 0.4 * (2.0 * time).cos(),
                    delta_time,
                };

                let (image_index, suboptimal, acquire_future): (u32, bool, SwapchainAcquireFuture) =
                    match acquire_next_image(swap_chain.clone(), None).map_err(Validated::unwrap) {
                        Ok(result) => result,
                        Err(VulkanError::OutOfDate) => {
                            recreate_swapchain = true;
                            return;
                        }
                        Err(error) => panic!("Failed to acquire next image error: {:?}", error),
                    };
                recreate_swapchain |= suboptimal;

                let builder: AutoCommandBufferBuilder<PrimaryAutoCommandBuffer> = AutoCommandBufferBuilder::primary(
                    &command_buffer_allocator,
                    queue.queue_family_index(),
                    CommandBufferUsage::OneTimeSubmit,
                )
                .expect("Unable to create AutoCommandBufferBuilder.");

                let command_buffer: Arc<PrimaryAutoCommandBuffer> = build_command_buffer(
                    &viewport,
                    &graphics_pipeline,
                    &compute_pipeline,
                    &frame_buffer,
                    &vertex_buffer,
                    &compute_descriptor_set,
                    push_constants,
                    image_index,
                    PARTICLE_COUNT,
                    builder,
                );

                let future: VulkanFuture = create_future(
                    previous_frame_end.take(),
                    acquire_future,
                    &queue,
                    &swap_chain,
                    command_buffer,
                    image_index,
                );

                match future.map_err(Validated::unwrap) {
                    Ok(future) => {
                        previous_frame_end = Some(future.boxed());
                    }
                    Err(VulkanError::OutOfDate) => {
                        recreate_swapchain = true;
                        previous_frame_end = Some(sync::now(logical_device.clone()).boxed());
                    }
                    Err(error) => {
                        println!("Failed to flush future error: {error}");
                        previous_frame_end = Some(sync::now(logical_device.clone()).boxed());
                    }
                }
                fps_counter.frame();
            }
            _ => {}
        },
    );
}

fn create_future(
    mut previous_frame_end: Option<Box<dyn GpuFuture>>,
    acquire_future: SwapchainAcquireFuture,
    queue: &Arc<Queue>,
    swap_chain: &Arc<Swapchain>,
    command_buffer: Arc<PrimaryAutoCommandBuffer>,
    image_index: u32,
) -> VulkanFuture {
    let swap_chain_info: SwapchainPresentInfo = SwapchainPresentInfo::swapchain_image_index(swap_chain.clone(), image_index);

    return previous_frame_end
        .take()
        .unwrap()
        .join(acquire_future)
        .then_execute(queue.clone(), command_buffer)
        .unwrap()
        .then_swapchain_present(queue.clone(), swap_chain_info)
        .then_signal_fence_and_flush();
}

fn create_compute_descriptor_set(
    descriptor_set_allocator: &StandardDescriptorSetAllocator,
    vertex_buffer: &Subbuffer<[Vertex]>,
    compute_pipeline: &Arc<ComputePipeline>,
) -> Arc<PersistentDescriptorSet<StandardDescriptorSetAlloc>> {
    let uniform_set_layout: &Arc<DescriptorSetLayout> = compute_pipeline.layout().set_layouts().get(0).unwrap();
    return PersistentDescriptorSet::new(
        descriptor_set_allocator,
        uniform_set_layout.clone(),
        [WriteDescriptorSet::buffer(0, vertex_buffer.clone())],
        [],
    )
    .expect("Unable to create compute pipeline descriptor set.");
}
