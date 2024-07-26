# Lectern snapshot

## Resource pack

`@resource_pack pack.mcmeta`

```json
{
  "pack": {
    "pack_format": 34,
    "description": "Ice who is overrided by Fire"
  }
}
```

### minecraft

`@fragment_shader(strip_final_newline) minecraft:core/rendertype_armor_cutout_no_cull`

```glsl
#version 150

#moj_import <fog.glsl>
#moj_import <light.glsl>

#define TEX_RES 16
#define ANIM_SPEED 50 // Runs every 24 seconds
#define IS_LEATHER_LAYER texelFetch(Sampler0, ivec2(0, 1), 0) == vec4(1) // If it's leather_layer_X.png texture

uniform sampler2D Sampler0;

uniform vec4 ColorModulator;
uniform float FogStart;
uniform float FogEnd;
uniform vec4 FogColor;
uniform float GameTime;
uniform vec3 Light0_Direction;
uniform vec3 Light1_Direction;

in float vertexDistance;
in vec4 vertexColor;
in vec2 texCoord0;
in vec2 texCoord1;
in vec4 normal;
flat in vec4 tint;
flat in vec3 vNormal;
flat in vec4 texel;

out vec4 fragColor;

void main()
{
    ivec2 atlasSize = textureSize(Sampler0, 0);
    float armorAmount = atlasSize.x / (TEX_RES * 4.0);
    float maxFrames = atlasSize.y / (TEX_RES * 2.0);

    vec2 coords = texCoord0;
    coords.x /= armorAmount;
    coords.y /= maxFrames;

    vec4 color;

    if(IS_LEATHER_LAYER)
    {
        // Texture properties contains extra info about the armor texture, such as to enable shading
        vec4 textureProperties = vec4(0);
        vec4 customColor = vec4(0);

        float h_offset = 1.0 / armorAmount;
        vec2 nextFrame = vec2(0);
        float interpolClock = 0;
        vec4 vtc = vertexColor;

        for (int i = 1; i < (armorAmount + 1); i++)
        {
            customColor = texelFetch(Sampler0, ivec2(TEX_RES * 4 * i + 0.5, 0), 0);
            if (tint == customColor){

                coords.x += (h_offset * i);
                vec4 animInfo = texelFetch(Sampler0, ivec2(TEX_RES * 4 * i + 1.5, 0), 0);
                animInfo.rgb *= animInfo.a * 255;
                textureProperties = texelFetch(Sampler0, ivec2(TEX_RES * 4 * i + 2.5, 0), 0);
                textureProperties.rgb *= textureProperties.a * 255;
                if (animInfo != vec4(0))
                {
                    // oh god it's animated
                    // animInfo = amount of frames, speed, interpolation (1||0)
                    // textureProperties = emissive, tint
                    // fract(GameTime * 1200) blinks every second so [0,1] every second
                    float timer = floor(mod(GameTime * ANIM_SPEED * animInfo.g, animInfo.r));
                    if (animInfo.b > 0)
                        interpolClock = fract(GameTime * ANIM_SPEED * animInfo.g);
                    float v_offset = (TEX_RES * 2.0) / atlasSize.y * timer;
                    nextFrame = coords;
                    coords.y += v_offset;
                    nextFrame.y += (TEX_RES * 2.0) / atlasSize.y * mod(timer + 1, animInfo.r);
                }
                break;
            }
        }

        if (textureProperties.g == 1)
        {
            if (textureProperties.r > 1)
            {
                vtc = tint;
            }
            else if (textureProperties.r == 1)
            {
                if (texture(Sampler0, vec2(coords.x + h_offset, coords.y)).a != 0)
                {
                    vtc = tint * texture(Sampler0, vec2(coords.x + h_offset, coords.y)).a;
                }
            }
        }
        else if(textureProperties.g == 0)
        {
            if (textureProperties.r > 1)
            {
                vtc = vec4(1);
            }
            else if (textureProperties.r == 1)
            {
                if (texture(Sampler0, vec2(coords.x + h_offset, coords.y)).a != 0)
                {
                    vtc = vec4(1) * texture(Sampler0, vec2(coords.x + h_offset, coords.y)).a;
                }
                else
                {
                    vtc = minecraft_mix_light(Light0_Direction, Light1_Direction, vNormal, vec4(1)) * texel;
                }
            }
            else
            {
                vtc = minecraft_mix_light(Light0_Direction, Light1_Direction, vNormal, vec4(1)) * texel;
            }
        }
        else
        {
            vtc = minecraft_mix_light(Light0_Direction, Light1_Direction, vNormal, vec4(1)) * texel;
        }

        vec4 armor = mix(texture(Sampler0, coords), texture(Sampler0, nextFrame), interpolClock);

        // If it's the first leather texture in the atlas (used for the vanilla leather texture, with no custom color specified)
        if (coords.x < (1 / armorAmount))
            color = armor * vertexColor * ColorModulator;
        else // If it's a custom texture
            color = armor * vtc * ColorModulator;
    }
    else // If it's another vanilla armor, for example diamond_layer_1.png or diamond_layer_2.png
    {
        color = texture(Sampler0, texCoord0) * vertexColor * ColorModulator;
    }

    if (color.a < 0.1)
        discard;

    fragColor = linear_fog(color, vertexDistance, FogStart, FogEnd, FogColor);
}
```

`@shader minecraft:core/rendertype_armor_cutout_no_cull`

```json
{
  "blend": {
    "func": "add",
    "srcrgb": "srcalpha",
    "dstrgb": "1-srcalpha"
  },
  "vertex": "rendertype_armor_cutout_no_cull",
  "fragment": "rendertype_armor_cutout_no_cull",
  "attributes": [
    "Position",
    "Color",
    "UV0",
    "UV1",
    "UV2",
    "Normal"
  ],
  "samplers": [
    {
      "name": "Sampler0"
    },
    {
      "name": "Sampler2"
    }
  ],
  "uniforms": [
    {
      "name": "ModelViewMat",
      "type": "matrix4x4",
      "count": 16,
      "values": [
        1.0,
        0.0,
        0.0,
        0.0,
        0.0,
        1.0,
        0.0,
        0.0,
        0.0,
        0.0,
        1.0,
        0.0,
        0.0,
        0.0,
        0.0,
        1.0
      ]
    },
    {
      "name": "ProjMat",
      "type": "matrix4x4",
      "count": 16,
      "values": [
        1.0,
        0.0,
        0.0,
        0.0,
        0.0,
        1.0,
        0.0,
        0.0,
        0.0,
        0.0,
        1.0,
        0.0,
        0.0,
        0.0,
        0.0,
        1.0
      ]
    },
    {
      "name": "ColorModulator",
      "type": "float",
      "count": 4,
      "values": [
        1.0,
        1.0,
        1.0,
        1.0
      ]
    },
    {
      "name": "Light0_Direction",
      "type": "float",
      "count": 3,
      "values": [
        0.0,
        0.0,
        0.0
      ]
    },
    {
      "name": "Light1_Direction",
      "type": "float",
      "count": 3,
      "values": [
        0.0,
        0.0,
        0.0
      ]
    },
    {
      "name": "FogStart",
      "type": "float",
      "count": 1,
      "values": [
        0.0
      ]
    },
    {
      "name": "FogEnd",
      "type": "float",
      "count": 1,
      "values": [
        1.0
      ]
    },
    {
      "name": "FogColor",
      "type": "float",
      "count": 4,
      "values": [
        0.0,
        0.0,
        0.0,
        0.0
      ]
    },
    {
      "name": "GameTime",
      "type": "float",
      "count": 1,
      "values": [
        1.0
      ]
    }
  ]
}
```

`@vertex_shader minecraft:core/rendertype_armor_cutout_no_cull`

```glsl
#version 150

#moj_import <light.glsl>

in vec3 Position;
in vec4 Color;
in vec2 UV0;
in vec2 UV1;
in ivec2 UV2;
in vec3 Normal;

uniform sampler2D Sampler2;

uniform mat4 ModelViewMat;
uniform mat4 ProjMat;

uniform vec3 Light0_Direction;
uniform vec3 Light1_Direction;

out float vertexDistance;
out vec4 vertexColor;
out vec2 texCoord0;
out vec2 texCoord1;
out vec4 normal;
flat out vec4 tint;
flat out vec3 vNormal;
flat out vec4 texel;

void main() {
    vNormal = Normal;
    texel = texelFetch(Sampler2, UV2 / 16, 0);
    gl_Position = ProjMat * ModelViewMat * vec4(Position, 1.0);

    vertexDistance = length((ModelViewMat * vec4(Position, 1.0)).xyz);
    vertexColor = minecraft_mix_light(Light0_Direction, Light1_Direction, Normal, Color) * texelFetch(Sampler2, UV2 / 16, 0);
    tint = Color;
    texCoord0 = UV0;
    texCoord1 = UV1;
    normal = ProjMat * ModelViewMat * vec4(Normal, 0.0);
}
```

`@texture minecraft:models/armor/leather_layer_1`

![texture.png](data:image/png;base64,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)

`@texture minecraft:models/armor/leather_layer_1_overlay`

![texture.png](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEAAAAAgCAYAAACinX6EAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAABNSURBVGhD7dAxAQAwDICwbv49tw8uIA8/b3fH7FOtBlCtBlCtBlCtBlCtBlCtBlCtBlCtBlCtBlCtBlCtBlCtBlCtBlCtBlCtBlCpmQMjogM92PpgGQAAAABJRU5ErkJggg==)

`@texture minecraft:models/armor/leather_layer_2`

![texture.png](data:image/png;base64,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)

`@texture minecraft:models/armor/leather_layer_2_overlay`

![texture.png](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEAAAAAgCAYAAACinX6EAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAABNSURBVGhD7dAxAQAwDICwbv49tw8uIA8/b3fH7FOtBlCtBlCtBlCtBlCtBlCtBlCtBlCtBlCtBlCtBlCtBlCtBlCtBlCtBlCtBlCpmQMjogM92PpgGQAAAABJRU5ErkJggg==)
