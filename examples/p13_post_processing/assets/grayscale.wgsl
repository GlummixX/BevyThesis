#import bevy_core_pipeline::fullscreen_vertex_shader::FullscreenVertexOutput

@group(0) @binding(0) var screen_texture: texture_2d<f32>;
@group(0) @binding(1) var texture_sampler: sampler;

@fragment
fn fragment(in: FullscreenVertexOutput) -> @location(0) vec4<f32> {
    var color: vec4<f32> = textureSample(screen_texture, texture_sampler, in.uv);
    
    // Convert to grayscale using standard luminance weights
    var gray: f32 = dot(color.rgb, vec3<f32>(0.299, 0.587, 0.114));
    
    return vec4<f32>(vec3<f32>(gray), color.a);
} 