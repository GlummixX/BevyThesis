#version 460

layout(location = 0) in vec2 position;
layout(location = 1) in vec2 velocity;

layout(location = 0) out vec4 outColor;

// A constant representing the maximum speed for normalization purposes.
const float maxSpeed = 10.0;

// Convert a hue value to RGB using the piecewise linear functions.
// This is a helper function for the HSL to RGB conversion.
float hue2rgb(float p, float q, float t) {
    t = fract(t);
    float sixT = 6.0 * t;
    // Perform the linear interpolation between p and q based on the scaled value of t.
    return mix(p, q, clamp((sixT < 1.0)? sixT : ((sixT < 3.0)? 1.0 : ((sixT < 4.0)? (4.0 - sixT) : 0.0)), 0.0, 1.0));
}

// Convert HSL color space to RGB color space.
vec3 hslToRgb(float h, float s, float l) {
    vec3 rgb = vec3(l);
    if (s != 0.0) {
        // Determine the intermediate values p and q for the conversion.
        float q = mix(l * (1.0 + s), l + s - l * s, step(l, 0.5));
        float p = 2.0 * l - q;

        // Convert HSL to RGB using the hue2rgb helper function.
        rgb.r = hue2rgb(p, q, h + 1.0 / 3.0);
        rgb.g = hue2rgb(p, q, h);
        rgb.b = hue2rgb(p, q, h - 1.0 / 3.0);
    }
    return rgb;
}

void main() {
    gl_PointSize = 1.0;
    gl_Position = vec4(position, 0.0, 1.0);

    // Calculate the speed based on the velocity, normalized by maxSpeed.
    float speed = length(velocity) / maxSpeed;
    // Convert the speed to a hue value and then to an RGB color.
    vec3 vibrantColor = hslToRgb(fract(speed), 1.0, 0.5);

    // Mix the color based on the position and calculated color, weighted by the speed.
    outColor = mix(
        // Base color dependent on position.
        vec4(0.8 * position, 1.0 - speed, 1.0),
        // Color dependent on speed.
        vec4(vibrantColor, 1.0),
        // Factor that determines the mix of the base and vibrant color.
        speed
    );
}
