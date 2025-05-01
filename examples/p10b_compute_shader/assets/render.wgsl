@location(0) var<in> position: vec2<f32>;
@location(1) var<in> velocity: vec2<f32>;

@location(0) var<out> outColor: vec4<f32>;

const maxSpeed: f32 = 10.0;

@vertex
fn vs_main() -> @builtin(position) vec4<f32> {
    return vec4<f32>(position, 0.0, 1.0);
}

@fragment
fn fs_main() -> @location(0) vec4<f32> {
    let speed = length(velocity) / maxSpeed;
    let color = mix(
        mix(vec3<f32>(0.0, 0.0, 1.0), vec3<f32>(0.0, 1.0, 0.0), clamp(speed * 2.0, 0.0, 1.0)),
        vec3<f32>(1.0, 0.0, 0.0),
        clamp((speed - 0.5) * 2.0, 0.0, 1.0)
    );
    return vec4<f32>(color, 1.0);
}
