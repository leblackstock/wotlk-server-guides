# WeakAuras Combat Cursor Ring and Flame Trail

This recipe creates a cursor-finder ring that appears only during combat and adds a connected gold-and-orange trail that tapers and fades after the cursor stops.

**Repository role:** Validated internal addon recipe. This is not a player-facing guide page and is not linked from the public Guide Hub.

Related repository content:

- [Addon Library guide](../../guides/addons.html)
- [Canonical addon catalog](../../data/addons.json)

## Compatibility

- World of Warcraft 3.3.5a
- WeakAuras 5.21.6, `X-Flavor: 3.3.5`
- NoM0Re/WeakAuras-WotLK build

The WeakAura draws around the native cursor; it does not replace the cursor.

## Base cursor ring

1. Open WeakAuras with `/wa`.
2. Select **New → Texture** and name it **Combat Cursor Finder**.
3. Under **Display**:
   - Choose a hollow circle or ring texture.
   - Set width and height to approximately `70–90`.
   - Expand **Position and Size Settings**.
   - Set **Anchored To → Mouse Cursor**.
   - Use centered positioning with `X: 0` and `Y: 0`.
   - Set opacity to approximately `70–80%`.
4. Under **Trigger**:
   - Select **Player/Unit Info → Conditions**.
   - Enable **Always active trigger**.
5. Under **Load**:
   - Set **In Combat** to green.
   - Optionally restrict the aura to **Class → Paladin**.

If **Mouse Cursor** is unavailable under **Anchored To**, verify that the texture is standalone rather than a child of a Dynamic Group.

## Flame trail

Select **Combat Cursor Finder → Actions**. Enable **Custom Init**, **Custom Load**, and **Custom Unload**, then paste the corresponding code below.

### Custom Init

```lua
local env = aura_env
local maxPoints = 28
local life = 0.28
local sampleRate = 0.012

-- Disable the earlier dotted-trail version if it exists.
if env.cursorTrailFrame then
    env.cursorTrailFrame:SetScript("OnUpdate", nil)
    env.cursorTrailFrame:Hide()
end

local frame = env.flameTrailFrame

if not frame then
    frame = CreateFrame("Frame", nil, UIParent)
    env.flameTrailFrame = frame
end

frame:SetAllPoints(UIParent)
frame:SetFrameStrata("HIGH")
frame.points = {}
frame.sprites = frame.sprites or {}
frame.elapsed = 0
frame.lastX = nil
frame.lastY = nil

for i = 1, maxPoints do
    local sprite = frame.sprites[i]

    if not sprite then
        sprite = {}

        sprite.glow = frame:CreateTexture(nil, "ARTWORK")
        sprite.glow:SetTexture(
            "Interface\\AddOns\\WeakAuras\\Media\\Textures\\Circle_Smooth.tga"
        )
        sprite.glow:SetBlendMode("ADD")

        sprite.core = frame:CreateTexture(nil, "OVERLAY")
        sprite.core:SetTexture(
            "Interface\\AddOns\\WeakAuras\\Media\\Textures\\Circle_Smooth.tga"
        )
        sprite.core:SetBlendMode("ADD")

        frame.sprites[i] = sprite
    end

    sprite.glow:Hide()
    sprite.core:Hide()
end

frame:SetScript("OnUpdate", function(self, elapsed)
    if not env.flameTrailActive then
        return
    end

    local points = self.points

    -- Age and remove old trail points.
    for i = 1, #points do
        points[i].age = points[i].age + elapsed
    end

    while #points > 0 and points[#points].age >= life do
        table.remove(points)
    end

    self.elapsed = self.elapsed + elapsed

    if self.elapsed >= sampleRate then
        self.elapsed = 0

        local x, y = GetCursorPosition()
        local scale = UIParent:GetEffectiveScale()

        x = x / scale
        y = y / scale

        if self.lastX then
            local dx = x - self.lastX
            local dy = y - self.lastY
            local distance = math.sqrt((dx * dx) + (dy * dy))

            if distance >= 2 then
                local steps = math.ceil(distance / 8)

                if steps > maxPoints then
                    steps = maxPoints
                end

                for step = 1, steps do
                    local progress = step / steps

                    table.insert(points, 1, {
                        x = self.lastX + (dx * progress),
                        y = self.lastY + (dy * progress),
                        age = 0
                    })
                end

                self.lastX = x
                self.lastY = y
            end
        else
            table.insert(points, 1, {
                x = x,
                y = y,
                age = 0
            })

            self.lastX = x
            self.lastY = y
        end

        while #points > maxPoints do
            table.remove(points)
        end
    end

    for i = 1, maxPoints do
        local point = points[i]
        local sprite = self.sprites[i]

        if point then
            local ageFade = 1 - (point.age / life)
            local tailFade = 1 - ((i - 1) / maxPoints)
            local fade = ageFade * tailFade

            local glowSize = 5 + (24 * fade)
            local coreSize = 2 + (9 * fade)

            sprite.glow:ClearAllPoints()
            sprite.glow:SetPoint(
                "CENTER", UIParent, "BOTTOMLEFT",
                point.x, point.y
            )
            sprite.glow:SetWidth(glowSize)
            sprite.glow:SetHeight(glowSize)
            sprite.glow:SetVertexColor(
                1, 0.20, 0.02, 0.38 * fade
            )
            sprite.glow:Show()

            sprite.core:ClearAllPoints()
            sprite.core:SetPoint(
                "CENTER", UIParent, "BOTTOMLEFT",
                point.x, point.y
            )
            sprite.core:SetWidth(coreSize)
            sprite.core:SetHeight(coreSize)
            sprite.core:SetVertexColor(
                1, 0.92, 0.35, 0.80 * fade
            )
            sprite.core:Show()
        else
            sprite.glow:Hide()
            sprite.core:Hide()
        end
    end
end)

frame:Hide()
```

### Custom Load

```lua
aura_env.flameTrailActive = true

local frame = aura_env.flameTrailFrame

if frame then
    frame.points = {}
    frame.elapsed = 0
    frame.lastX = nil
    frame.lastY = nil
    frame:Show()
end
```

### Custom Unload

```lua
aura_env.flameTrailActive = false

local frame = aura_env.flameTrailFrame

if frame then
    frame:Hide()
    frame.points = {}

    for i = 1, #frame.sprites do
        frame.sprites[i].glow:Hide()
        frame.sprites[i].core:Hide()
    end
end
```

After saving the three actions, close `/wa` and run `/reload` once.

## Tuning

- Trail length: increase or decrease `maxPoints = 28`.
- Fade duration: increase or decrease `life = 0.28`.
- Sampling frequency: decrease `sampleRate = 0.012` for a denser trail; lower values perform more work.
- Outer flame color: edit `1, 0.20, 0.02` in `sprite.glow:SetVertexColor`.
- Core color: edit `1, 0.92, 0.35` in `sprite.core:SetVertexColor`.
- Flame width: edit the `glowSize` and `coreSize` calculations.

## Verification

- Out of combat: the ring and trail are hidden.
- In combat: the ring follows the native cursor.
- While moving the cursor: the trail forms a connected, tapered flame.
- When the cursor stops: the trail fades within approximately `0.28` seconds.
- When combat ends: the ring and trail disappear.

## Removal

To remove only the trail, disable **Custom Init**, **Custom Load**, and **Custom Unload**, then run `/reload`. To remove the complete cursor finder, delete the **Combat Cursor Finder** aura.
