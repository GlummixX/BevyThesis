#version 460

layout(local_size_x = 256, local_size_y = 1, local_size_z = 1) in;

struct VertexData {
    vec2 position;
    vec2 velocity;
};

layout (binding = 0) buffer VertexBuffer {
    VertexData verticies[];
};

layout (push_constant) uniform PushConstants {
    vec2 attractor;
    float attractor_strength;
    float delta_time;
} push;

const float maxSpeed = 12.0;
const float minLength = 0.03;
const float friction = -1.5;

void main() {
    const uint index = gl_GlobalInvocationID.x;

    vec2 velocity = verticies[index].velocity;
    vec2 position = verticies[index].position + push.delta_time * velocity;

    if (abs(position.x) > 1.0) {
        velocity.x = sign(position.x) * (-0.95 * abs(velocity.x) - 0.0001);
        position.x = min(max(position.x, -1.0), 1.0);
    }
    if (abs(position.y) > 1.0) {
        velocity.y = sign(position.y) * (-0.95 * abs(velocity.y) - 0.0001);
        position.y = min(max(position.y, -1.0), 1.0);
    }

    vec2 t = push.attractor - position;
    float r = max(length(t), minLength);
    vec2 force = push.attractor_strength * (t / r) / (r * r);

    velocity += push.delta_time * force;
    velocity = (length(velocity) > maxSpeed)? maxSpeed * normalize(velocity) : velocity;

    verticies[index].position = position;
    verticies[index].velocity = velocity * exp(friction * push.delta_time);
}