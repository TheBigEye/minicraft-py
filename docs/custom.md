# Custom Content

## What Are Mods?

The game allows you to modify various aspects of its content without needing to know how to program. You can change how things look, create your own worlds, add new types of tiles, and even modify the player attributes. While these features are still experimental, they're designed to be easy to use and understand.

## The "Great" Manifest File

At the heart of every mod is a file called `manifest.json`. Think of it as a recipe book that tells the game what changes you want to make. This file needs to be placed in a folder called `mods` where your game is installed. Here's a simple example:

```json
{
    "name": "My First Mod",
    "version": "1.0.0",
    "description": "This is my awesome mod",

    "custom_tilemap": {
        "#0F0F0F": {
            "name": "hard_rock",
            "id": 9,
            "liquid": false,
            "solid": true,
            "health": -1,
            "parent": 1,
            "sprites": [[19, 1]]
        }
    },

    "custom_player": {
        "spawn": [8.00, 8.00]
    }
}
```

Every manifest needs three basic pieces of information:
- A name for your mod
- A version number
- A description of what your mod does

## Changing How Things Look

The game uses a single image file called an "atlas" that contains all the game's graphics. If you want to change how things look in the game, you can create your own version of this image. Here's how:

1. Find the original `atlas.png` in the game's assets folder
2. Make a copy of it
3. Edit the copy to change the graphics
4. Save your modified version as `atlas.png` in the `mods` folder

Important: Your new atlas image should not be smaller than the original one. The game uses magenta (*bright pink*, **#FF00FF**) as a transparent color, so don't use that color in your graphics.

## Creating Your Own World

> **NOTE:** Adding a custom atlas will still allow you to play in your previously saved normal world, but a full mod that includes a custom world will not. So, only as long as you have your custom world inside the mods folder, the game will only allow you to play that world

You can design your own world using a `world.png` image. The game divides your world into sections called "chunks", each being 8x8 tiles in size. If your world's dimensions aren't multiples of 8, the game will automatically fill incomplete chunks with grass tiles. For example, a 10x10 world will effectively become 16x16, with grass filling the extra space:

This might look something like this:
```
Your 10x10 world:              Actual 16x16 (with grass fill):
##~~                           ##~~####
##~~                           ##~~####
....      will become →        ....####
....                           ....####
                               ########
                               ########
```

> **INFO:** Custom worlds typically perform better than normal worlds since they don't need to generate terrain on the fly.

### Available Tiles

| **ID** | **Color**   | **Tile**    | **Solid?** | **Liquid?** | **Parent ID** | **Parent Name** | **Health** |
|--------|:-----------:|-------------|:----------:|:-----------:|:-------------:|-----------------|:----------:|
| 0      | `#0000FF`   | Water       | False      | True        | -1            | None            | -1         |
| 1      | `#E2C363`   | Sand        | False      | False       | 2             | Dirt            | 1          |
| 2      | `#654321`   | Dirt        | False      | False       | 3             | Hole            | 1          |
| 3      | `#808080`   | Hole        | False      | False       | -1            | None            | -1         |
| 4      | `#69CC00`   | Grass       | False      | False       | 2             | Dirt            | 1          |
| 5      | `#FFFF00`   | Flowers     | False      | False       | 4             | Grass           | 1          |
| 6      | `#417F00`   | Oak Tree    | True       | False       | 2             | Dirt            | 16         |
| 7      | `#419B00`   | Birch Tree  | True       | False       | 2             | Dirt            | 18         |
| 8      | `#41B200`   | Pine Tree   | True       | False       | 2             | Dirt            | 24         |
| 9      | `#565656`   | Stone       | True       | False       | 2             | Dirt            | 24         |
| 10     | `#C8C8FA`   | Ice         | False      | False       | 0             | Water           | 4          |
| 11     | `#FAFAFF`   | Snow        | False      | False       | 2             | Dirt            | 1          |
| 12     | `#DCDCFF`   | Iceberg     | True       | False       | 0             | Water           | 8          |
| 13     | `#00FF00`   | Cactus      | True       | False       | 1             | Sand            | 8          |
| 14     | `#878787`   | Iron Ore    | True       | False       | 2             | Dirt            | 26         |


## Custom Content Dependencies

It's important to understand that some custom features depend on others to work:

1. **Custom World Requirement**
   - Custom tiles will only work if you have a custom world file (`world.png`)
   - Player spawn customization also needs a custom world to function

2. **Custom Atlas (Optional)**
   - If you want your custom tiles to have unique appearances, you'll need a custom atlas
   - Without a custom atlas, your tiles will use graphics from the original game

## Creating Custom Tiles

Custom tiles are perhaps the most powerful feature. Each tile in your custom tilemap needs a unique color code and some basic properties. The name and ID are always required, but when you're modifying an existing tile (using a known ID), you only need to specify the properties you want to change. However, if you're creating a completely new tile with a new ID, you must define all properties.

### Basic Properties

When creating a custom tile in your manifest, each tile needs:
```json
"#0F0F0F": {
    "name": "hard_rock",
    "id": 9,
    "liquid": false,
    "solid": true,
    "health": -1,
    "parent": 1,
    "sprites": [
        [19, 1],
        // ...
    ]
}
```

- `"#0F0F0F"`: The hexadecimal color value that represents your tile in world.png (you can override an existing base tile, but must be unique for custom tiles)
- `name`: A name for your tile (currently used for debugging, also good for organization)
- `id`: A unique number for your tile. If you use an ID that already exists in the game, your tile will replace it
- `liquid`: Makes the tile behave like a liquid - players can swim in it and it might spread
- `solid`: Determines if players can walk through the tile
- `health`: How many hits it takes to break the tile (-1 makes it unbreakable)
- `parent`: Which tile should appear when this one is destroyed (use the ID number of that tile)

### Advanced Graphics (Sprites)

The `sprites` section supports three different formats for defining sprite coordinates, giving you more control over how your tiles look, but also it's crucial to understand that you can only use one format at a time for each tile.

1. Basic Format (2 values)
   ```json
   "sprites": [[0, 1]]  // [x, y]
   ```
   This is the simplest format. It assumes:
   - The sprite is 16x16 pixels
   - Will be scaled to `TILE_SIZE` (32 pixels)
   - Coordinates are multiplied by 16 to find the position in the atlas
   - This is the only format that supports tile-blending

2. Extended Format (4 values)
   ```json
   "sprites": [[0, 1, 32]]  // [x, y, size]
   ```
   This format gives you control over:
   - `x, y`: Position in the atlas grid
   - `size`: Size of the grid cells (e.g., 32 for 32x32 sprites)
   The final tile will be scaled by `size * 2`
   Perfect for larger tiles like trees.

3. Pixel-Precise Format (5 values)
   ```json
   "sprites": [[0, 1, 24, 24, 2]]  // [x, y, width, height, scale_factor]
   ```
   This format gives you complete control:
   - `x, y`: Exact pixel coordinates in the atlas
   - `width, height`: Exact size of the sprite in pixels
   - `scale_factor`: Multiplier for `TILE_SIZE` (e.g., 2 means 2×TILE_SIZE)
   Ideal for sprites that don't fit the standard grid.

Example using different formats:

```json
{
    "custom_tilemap": {
        "#AFAFAF": {
            "name": "mixed_tile",
            "id": 100,
            "liquid": false,
            "solid": true,
            "health": 100,
            "parent": 0,
            "sprites": [
                [0, 1],                 // Basic 16x16 sprite
                [0, 2, 32],             // 32x32 sprite
                [128, 64, 24, 24, 2]    // 24x24 sprite from exact position, scaled 2x
            ]
        }
    }
}
```

The game uses a specific order for sprite transitions to make tiles blend naturally with their surroundings:

1. Base Appearance (Required)
   ```json
   "sprites": [[19, 1]]  // Just the basic look
   ```

2. Adding Transitions (Optional)
   ```json
   "sprites": [
        [19, 1],  // Base look

        // Edges
        [19, 0],  // Top edge
        [20, 1],  // Left edge
        [18, 1],  // Right edge
        [19, 2]   // Bottom edge

        // Corners
        [18, 0],  // Top-left corner
        [20, 0],  // Top-right corner
        [18, 2],  // Bottom-left corner
        [20, 2]   // Bottom-right corner
    ]
   ```

3. Adding Variety (Makes large areas look less repetitive)
   ```json
   "sprites": [
       // [Previous sprites...],
       [20, 3],  // Alternative look 1
       [20, 4]   // Alternative look 2
   ]
   ```

5. Adding Depth (Makes tiles look more 3D)
   ```json
   "sprites": [
       // [Previous sprites...],
       [18, 3],  // Inner corner 1
       [19, 3],  // Inner corner 2
       [18, 4],  // Inner corner 3
       [19, 4]   // Inner corner 4
   ]
   ```

Each pair of numbers `[x, y]` tells the game where to find the 16x16 pixel graphic in your atlas image. The game automatically knows what to do based on how many sprites you provide:
- **1 sprite:** Tile tile with no special features
- **9 sprites:** Tile with transitions
- **11 sprites:** Tile with edges, corners, and random variations
- **15 sprites:** Complete tile with all features including depth

**Remember:** You don't need to use all these features. A simple tile can work with just one sprite. Add more sprites only when you want your tile to look more polished and integrate better with its surroundings.

> **NOTE:** If the tile sprite is larger than the size of a normal tile, for example, 32 pixels, then the game will render it with depth just like the trees

## Customizing the Player

For now, you can only choose where your player starts in the world by adding a `"custom_player"` section to your manifest:

```json
{
    "custom_player": {
        "spawn": [8.00, 8.00]
    }
}
```

The numbers represent the `x` and `y` coordinates where your player will appear when starting the game.

> **NOTE:** Unlike normal worlds which allow negative coordinates, custom worlds require spawn points to be positive and within the world boundaries

## Organizing Your Mod Files

Keep your mod files organized in a `mods` folder with your manifest.json, atlas.png (if you're changing graphics), and world.png (if you're making a custom world). The game will automatically create a saves folder to store your progress.

Your mod files should be organized like this:
```
mods/
    manifest.json    (your mod's settings)
    atlas.png        (if you're changing graphics)
    world.png        (if you're making a custom world)
    saves/           (created automatically to save your progress)
```

If something isn't working, here are common issues to check:

**File-Related:**
- Verify all file names are exactly correct (including lowercase and uppercase letters)
- Make sure your manifest.json is properly formatted and has no typing mistakes
- Try deleting the "/saves/region" folder if you've changed your world

**Content-Related:**
- Check that your custom tile colors aren't already used by the game
- Verify spawn points are inside your world boundaries
- Make sure your atlas modifications maintain proper transparency


## Getting Started

The easiest way to start modding is to:
1. Create a `mods` folder
2. Create a simple manifest file with just the basic information
3. Try adding a custom world file
4. Test the game to make sure it works
5. Gradually add more features as you get comfortable


> Remember that modding is about experimenting and having fun :D
