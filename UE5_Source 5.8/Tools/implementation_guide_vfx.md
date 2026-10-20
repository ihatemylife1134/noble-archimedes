# VFX Implementation Guide

Complete implementation guide for Niagara particle systems in UE5.

## 1. VFX Component Setup

### 1.1 Create Component Blueprint
1. In UE5 Editor, right-click in Content Browser
2. Select **Blueprint Class**
3. Select `NobleArchimedesVFXComponent` as parent class
4. Name it `BP_VFXComponent`
5. Save to `Content/Blueprints/VFX/`

### 2. Niagara System Specifications

| System | Type | Particles | Lifetime | Size | Color |
|--------|------|-----------|----------|------|-------|
| NS_WeaponTrail_Sword | Ribbon | 10-20 | 0.3s | 10→0 | Silver |
| NS_WeaponTrail_Axe | Ribbon | 10-20 | 0.4s | 15→0 | Bronze |
| NS_WeaponTrail_Spear | Ribbon | 5-10 | 0.2s | 5→0 | Iron |
| NS_WeaponTrail_Knuckles | Ribbon | 5-10 | 0.15s | 8→0 | Steel |
| NS_WeaponTrail_Special | Ribbon | 15-25 | 0.5s | 12→0 | Gold |
| NS_HitSpark_Fire | Sprite burst | 5-10 | 0.2-0.4s | 5-15 UU | Orange→Red |
| NS_HitSpark_Ice | Sprite burst | 5-10 | 0.2-0.4s | 5-15 UU | Light Blue→White |
| NS_HitSpark_Light | Sprite burst | 8-12 | 0.1-0.3s | 5-15 UU | Yellow→White |
| NS_HitSpark_Dark | Sprite burst | 5-10 | 0.3-0.5s | 5-15 UU | Purple→Black |
| NS_HitBlood | Sprite burst | 3-6 | 0.5-1.0s | 3-8 UU | Dark Red→Brown |
| NS_QuickStepTrail | Ribbon + Sprite | 10-20 | 0.3s | 20→5 | White→Transparent |
| NS_PerfectGuardFlash | Sphere + Ring | N/A | 0.2s | 50→100 UU | Gold→White |
| NS_GuardBlockFlash | Ring | N/A | 0.15s | 30→60 UU | Silver→Transparent |
| NS_InnocentDevilSummon | Sprite + Light | 20 sparkles | 1.0s | N/A | Light Blue→White |
| NS_InnocentDevilEvolve | Sphere burst + Light | N/A | 1.5s | 100→200 UU | Gold→White |
| NS_InnocentDevilAttack | Sprite trail | N/A | 0.4s | N/A | Type Color→Transparent |
| NS_ItemPickup | Sprite + Light | 5 sparkles | 0.5s | N/A | Yellow→White |
| NS_CandleBreak | Sprite burst | 15-20 | 0.5-1.0s | N/A | Orange→Yellow |
| NS_SaveRoomHeal | Sphere glow + Sprite | N/A | 2.0s | 200 UU | Green→Light Green |

## 2. Niagara Parameters

### 2.1 Exposed Parameters
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| VFXScale | Float | 1.0 | Overall particle scale |
| ColorOverride | LinearColor | White | Override particle color |
| LifetimeMultiplier | Float | 1.0 | Scale particle lifetime |
| SpawnRate | Float | 1.0 | Particles per second |

### 2.2 Parameter Usage
```cpp
// Example: Spawn weapon trail with custom color
UNiagaraSystem* TrailSystem = NS_WeaponTrail_Sword;
UNiagaraComponent* TrailComponent = UNiagaraFunctionLibrary::SpawnSystemAtLocation(
    GetWorld(),
    TrailSystem,
    Location,
    Rotator
);
if (TrailComponent)
{
    TrailComponent->SetNiagaraVariableVec3("ColorOverride", WeaponColor);
    TrailComponent->SetNiagaraVariableFloat("VFXScale", 1.0f);
}
```

## 3. VFX Component Functions

### 3.1 Weapon Trail
```cpp
void UNobleArchimedesVFXComponent::PlayWeaponTrail(EWeaponType WeaponType, FVector StartLocation, FVector EndLocation)
{
    UNiagaraSystem* TrailSystem = nullptr;
    switch (WeaponType)
    {
        case EWeaponType::Sword: TrailSystem = NS_WeaponTrail_Sword; break;
        case EWeaponType::Axe: TrailSystem = NS_WeaponTrail_Axe; break;
        case EWeaponType::Spear: TrailSystem = NS_WeaponTrail_Spear; break;
        case EWeaponType::Knuckles: TrailSystem = NS_WeaponTrail_Knuckles; break;
        case EWeaponType::Special: TrailSystem = NS_WeaponTrail_Special; break;
    }
    
    if (TrailSystem)
    {
        UNiagaraComponent* Trail = UNiagaraFunctionLibrary::SpawnSystemAtLocation(
            GetWorld(),
            TrailSystem,
            StartLocation,
            FRotator::ZeroRotator
        );
        if (Trail)
        {
            Trail->SetNiagaraVariableFloat("VFXScale", VFXScale);
        }
    }
}
```

### 3.2 Hit Spark
```cpp
void UNobleArchimedesVFXComponent::PlayHitSpark(FVector Location, EDamageType DamageType)
{
    UNiagaraSystem* SparkSystem = nullptr;
    switch (DamageType)
    {
        case EDamageType::Fire: SparkSystem = NS_HitSpark_Fire; break;
        case EDamageType::Ice: SparkSystem = NS_HitSpark_Ice; break;
        case EDamageType::Light: SparkSystem = NS_HitSpark_Light; break;
        case EDamageType::Dark: SparkSystem = NS_HitSpark_Dark; break;
        default: SparkSystem = NS_HitSpark_Fire; break;
    }
    
    if (SparkSystem)
    {
        UNiagaraFunctionLibrary::SpawnSystemAtLocation(GetWorld(), SparkSystem, Location);
    }
}
```

## 4. Particle Performance

### 4.1 Particle Budget
| System | Max Particles | LOD Distance |
|--------|--------------|--------------|
| Weapon Trails | 500 per weapon | 1000 UU |
| Hit Sparks | 100 per hit | 500 UU |
| Companion VFX | 200 per companion | 800 UU |
| Ambient VFX | 100 per scene | 1500 UU |

### 4.2 Optimization Tips
- Use GPU particles for simple sprites
- Use CPU particles for complex interactions
- Disable particles when camera > 1000 UU away
- Set appropriate LOD distances
- Limit particle count per system

## 5. Testing Checklist

- [ ] All weapon trails spawn correctly
- [ ] All hit sparks spawn correctly
- [ ] All companion VFX spawn correctly
- [ ] All item VFX spawn correctly
- [ ] All environmental VFX spawn correctly
- [ ] VFX scale correctly with VFXScale parameter
- [ ] VFX don't cause performance issues
- [ ] VFX disappear when out of range
- [ ] VFX sync with animations correctly
