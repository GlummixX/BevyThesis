# Work in progress Bevy thesis

- p00_window - Základy vytváření a manipulace s okny, práce s knihovnou Winit
- p01_basic_triangle - Implementace základní vykreslovací smyčky, tvorba a načtení fragment a vertex shaderů
- p02_uniform_buffer - Práce s uniform buffery a push constants, zasílání dat do shaderů, základy práce s knihovnou cgmath
- p03_geometry - Výpočet viditelnosti za pomoci Z-bufferu, implementace index bufferu, definování různých 3D objektů (solidů)
- p04_textures - Načítání a mapování textur na různé objekty (solidy)
- p05_camera - Implementace kamery
- p06_obj - Načítání 3D modelů uložených ve formátu OBJ
- p07a_loop_rendering, p07b_instancing, p07c_offset_rendering - Implementace různých technik pro vykreslování více objektů (solidů) najednou
- p08_light - Implementace Phongova osvětlovacího modelu a práce s materiály
- p09_texture_array - Základy práce s polem textur, mapování textur na více objektů najednou
- p10a_compute_shader - Implementace základní compute pipeline, provádění výpočtů na grafické kartě
- p10b_compute_shader - Použití compute shaderů v kombinaci s vykreslovacím řetězcem (implementace částicového systému)
- p11_geometry_shader - Úvod do práce s geometry shadery
- p12_multiple_shaders - Načítání a použití shaderů uložených ve formátu SPIR-V, vykreslení objektů za pomoci několika fragment shaderů
- p13_post_processing - Post-processing základy techniky vykreslování do textury, základy víceprůchodového zpracování
- p14a_tessellation - p14b_tessellation - Úvod do práce s teselačními shadery, použití teselačních shaderů pro zvýšení detailů geometrie
- p15a_deferred_shading - p15b_deferred_shading - Rozdílné způsoby implementace techniky deferred shading, víceprůchodové zpracování

https://theses.cz/id/il01k0/?zpet=%2Fvyhledavani%2F%3Fsearch%3DAPI%20Vulkan%26start%3D1;isshlret=API%3BVulkan%3B


## Návod na spuštění ukázek
Návod předpokládá, že máte nainstalovaný jazyk rust a potřebné nástroje. Pokud ne, najdete návod na instalaci [zde](https://www.rust-lang.org/tools/install). <br>
Příkazový řadek musí být v adresáři examples, nikoliv v kořenovém adresáři repozitáře.

Pomocí následujícího příkazu můžete zkompilovat spustit libovolnou ukázku:
```bash
cargo run --bin <název_složky_ukázky>
```
Například: 
```bash
cargo run --bin p01_basic_triangle
```

Pro maximální výkon je potřeba spustit ukázku v řežimu release pomocí parametru `-r`: <br>
*Kompilace v režimu release může trvat déle v závislosti na HW.*
```bash
cargo run -r --bin <název_složky_ukázky>
```

Pokud chcete ukázku pouze zkompilovat bez spuštění, použijte příkaz `build` v kombinaci s parametrem `-r` pro optimalizovaný release:
```bash
cargo build -r --bin <název_složky_ukázky>
```
Výsledný binární soubor bude umístěn do složky `examples/target/release`.
Pokud byl soubor kompilován bez parametru `-r`, bude umístěn do složky `examples/target/debug`.