struct VertexData {
    pos: vec2<f32>,
    vel: vec2<f32>,
};

struct PushConstants {
    attr: vec2<f32>,
    attr_strength: f32,
    delta_t: f32,
};

@group(0) @binding(0)
var<storage, read_write> verticies: array<VertexData>;

@group(0) @binding(1)
var<uniform> push: PushConstants;

const maxSpeed: f32 = 10.0;
const minLength: f32 = 0.1;
const friction: f32 = -1;

@compute @workgroup_size(256, 1, 1)
fn main(@builtin(global_invocation_id) GlobalInvocationID: vec3<u32>) {
    let index: u32 = GlobalInvocationID.x;

    var vel: vec2<f32> = verticies[index].vel;
    var pos: vec2<f32> = verticies[index].pos + push.delta_t * vel;

    if (abs(pos.x) > 1.0) {
        vel.x = sign(pos.x) * (-0.95 * abs(vel.x) - 0.0001);
        pos.x = clamp(pos.x, -1.0, 1.0);
    }

    if (abs(pos.y) > 1.0) {
        vel.y = sign(pos.y) * (-0.95 * abs(vel.y) - 0.0001);
        pos.y = clamp(pos.y, -1.0, 1.0);
    }

    let t: vec2<f32> = push.attr - pos;
    let r: f32 = max(length(t), minLength);
    let force: vec2<f32> = push.attr_strength * (t / r) / (r * r);

    vel = vel + push.delta_t * force;

    if (length(vel) > maxSpeed) {
        vel = maxSpeed * normalize(vel);
    }

    verticies[index].pos = pos;
    verticies[index].vel = vel * exp(friction * push.delta_t);
}
