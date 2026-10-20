# Audio Implementation Guide

Complete implementation guide for the audio system in UE5.

## 1. Audio Components

### 1.1 Audio Component Setup
1. In UE5 Editor, right-click in Content Browser
2. Select **Blueprint Class**
3. Select `NobleArchimedesAudioComponent` as parent class
4. Name it `BP_AudioComponent`
5. Save to `Content/Blueprints/Audio/`

### 2. Audio Settings
| Setting | Default | Range | Description |
|---------|---------|-------|-------------|
| Master Volume | 1.0 | 0.0-1.0 | Overall volume |
| SFX Volume | 1.0 | 0.0-1.0 | Sound effects |
| Music Volume | 0.7 | 0.0-1.0 | Background music |
| 3D Audio | On | On/Off | Spatial audio |
| Occlusion | On | On/Off | Sound through walls |

## 3. Audio Cue Implementation

### 3.1 Combat SFX
Create Sound Cues in `Content/Audio/SFX/`:
- `SC_Combat_Swing_Sword` - Sword swing whoosh
- `SC_Combat_Swing_Axe` - Axe swing whoosh
- `SC_Combat_Swing_Spear` - Spear thrust whoosh
- `SC_Combat_Swing_Knuckles` - Punch whoosh
- `SC_Combat_Swing_Special` - Projectile whoosh
- `SC_Combat_WeaponHit` - Weapon hit impact
- `SC_Combat_PlayerHit` - Player takes damage
- `SC_Combat_EnemyHit` - Enemy takes damage
- `SC_Combat_QuickStep` - Dodge roll sound
- `SC_Combat_GuardBlock` - Guard block sound
- `SC_Combat_PerfectGuard` - Perfect guard parry
- `S_Combat_BossTheme` - Boss battle music

### 3.2 Item SFX
- `SC_Item_Pickup` - Generic item pickup
- `SC_Item_Potion` - Drink potion
- `SC_Item_HighPotion` - Drink high potion
- `SC_Item_Serum` - Use serum
- `SC_Item_Uncurse` - Remove curse
- `SC_Item_Steal` - Successful steal

### 3.3 UI Audio
- `SC_UI_Click` - Button click
- `SC_UI_MenuOpen` - Menu opens
- `SC_UI_Save` - Game saved

### 3.4 Ambient Audio (per chapter)
- `SC_Amb_Castle` - Chapter 1
- `SC_Amb_Mountains` - Chapter 2
- `SC_Amb_Temple` - Chapter 3
- `SC_Amb_Aqueduct` - Chapter 4
- `SC_Amb_Forest` - Chapter 5
- `SC_Amb_Town` - Chapter 6
- `SC_Amb_Tower` - Chapter 7
- `SC_Amb_Ruins` - Chapter 8
- `SC_Amb_Corridor` - Chapter 9
- `SC_Amb_CastleFinal` - Chapter 10

### 3.5 Music
- `SC_Music_Chap01` through `SC_Music_Chap10` - Chapter music
- `SC_Music_Combat` - Combat music
- `SC_Music_Boss` - Boss battle music
- `S_Music_Victory` - Victory fanfare
- `S_Music_GameOver` - Game over theme

## 4. Audio Implementation

### 4.1 Play Combat Sound
```cpp
void UNobleArchimedesAudioComponent::PlayWeaponSwing(EWeaponType WeaponType)
{
    USoundCue* SoundCue = nullptr;
    switch (WeaponType)
    {
        case EWeaponType::Sword: SoundCue = SC_Combat_Swing_Sword; break;
        case EWeaponType::Axe: SoundCue = SC_Combat_Swing_Axe; break;
        case EWeaponType::Spear: SoundCue = SC_Combat_Swing_Spear; break;
        case EWeaponType::Knuckles: SoundCue = SC_Combat_Swing_Knuckles; break;
        case EWeaponType::Special: SoundCue = SC_Combat_Swing_Special; break;
    }
    
    if (SoundCue)
    {
        UGameplayStatics::PlaySoundAtLocation(GetWorld(), SoundCue, GetOwner()->GetActorLocation(), SFXVolume);
    }
}
```

### 4.2 Play Ambient Audio
```cpp
void UNobleArchimedesAudioComponent::PlayAmbient(int32 ChapterIndex)
{
    USoundCue* AmbientCue = nullptr;
    switch (ChapterIndex)
    {
        case 1: AmbientCue = SC_Amb_Castle; break;
        case 2: AmbientCue = SC_Amb_Mountains; break;
        case 3: AmbientCue = SC_Amb_Temple; break;
        case 4: AmbientCue = SC_Amb_Aqueduct; break;
        case 5: AmbientCue = SC_Amb_Forest; break;
        case 6: AmbientCue = SC_Amb_Town; break;
        case 7: AmbientCue = SC_Amb_Tower; break;
        case 8: AmbientCue = SC_Amb_Ruins; break;
        case 9: AmbientCue = SC_Amb_Corridor; break;
        case 10: AmbientCue = SC_Amb_CastleFinal; break;
    }
    
    if (AmbientCue)
    {
        UGameplayStatics::PlaySoundAtLocation(GetWorld(), AmbientCue, GetOwner()->GetActorLocation(), MusicVolume);
    }
}
```

### 4.3 Volume Control
```cpp
void UNobleArchimedesAudioComponent::SetMasterVolume(float Volume)
{
    MasterVolume = FMath::Clamp(Volume, 0.0f, 1.0f);
    ApplyVolumeSettings();
}

void UNobleArchimedesAudioComponent::ApplyVolumeSettings()
{
    // Apply volume settings to sound mixer
    // This would set the mix volume for each sound class
}
```

## 5. Audio Settings Menu

### 5.1 Settings Widget
Create `WB_AudioSettings` widget with:
- Master Volume slider
- SFX Volume slider
- Music Volume slider
- 3D Audio toggle
- Occlusion toggle

### 5.2 Settings Logic
```cpp
void UNobleArchimedesAudioComponent::SetMasterVolume(float Volume)
{
    MasterVolume = FMath::Clamp(Volume, 0.0f, 1.0f);
    ApplyVolumeSettings();
    // Save to save game
    if (UNobleArchimedesSaveGame* SaveGame = Cast<UNobleArchimedesSaveGame>(UGameplayStatics::CreateSaveGameObject(UNobleArchimedesSaveGame::StaticClass())))
    {
        SaveGame->MasterVolume = MasterVolume;
    }
}
```

## 6. Testing Checklist

- [ ] All combat sounds play correctly
- [ ] All item sounds play correctly
- [ ] All UI sounds play correctly
- [ ] All ambient sounds play correctly
- [ ] All music tracks play correctly
- [ ] Volume controls work
- [ ] 3D audio spatialization works
- [ ] Occlusion works
- [ ] Audio persists across chapters
- [ ] Audio stops when game is paused
