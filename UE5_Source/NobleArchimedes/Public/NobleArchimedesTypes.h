// Fill out your copyright notice in the Description page of Project Settings.

#pragma once

#include "CoreMinimal.h"
#include "NobleArchimedesTypes.generated.h"

//=============================================================================
// ENUMS
//=============================================================================

UENUM(BlueprintType)
enum class ECombatState : uint8
{
	Idle,
	LightAttack1,
	LightAttack2,
	LightAttack3,
	HeavyAttack,
	QuickStep,
	Guard,
	PerfectGuard,
	Stunned,
	Dead
};

UENUM(BlueprintType)
enum class EWeaponType : uint8
{
	Sword,
	Axe,
	Spear,
	Knuckles,
	Special,
	None
};

UENUM(BlueprintType)
enum class EDamageType : uint8
{
	Fire,
	Ice,
	Light,
	Dark,
	Poison,
	Curse,
	Paralyze,
	Stone,
	Slash,
	Blunt,
	Magic,
	None
};

UENUM(BlueprintType)
enum class ECameraMode : uint8
{
	Classic,      // 4.2 UU distance, 70° FOV - original PS2 feel
	ActionOrbit,  // 3.6 UU distance, 78° FOV - modern action RPG
	OverTheShoulder // 1.75 UU distance, 65° FOV - precision aim
};

UENUM(BlueprintType)
enum class EInnocentDevilMode : uint8
{
	Auto,
	Command,
	Guard
};

UENUM(BlueprintType)
enum class EInnocentDevilType : uint8
{
	Fairy,
	Griffin,
	Salamander,
	Ogre,
	Skeleton,
	Witch,
	Pumpkin, // Secret Innocent Devil
	Light,
	Dark,
	Fire,
	Ice,
	None
};

//=============================================================================
// DATA STRUCTURES (Blueprint-accessible)
//=============================================================================

USTRUCT(BlueprintType)
struct FComboWindow
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Combat")
	float WindowDuration = 0.35f; // Time to input next attack

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Combat")
	float FinalAttackTiming = 0.15f; // Window to press final attack after strike
};

USTRUCT(BlueprintType)
struct FWeaponData
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Weapon")
	FName WeaponName;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Weapon")
	EWeaponType WeaponType = EWeaponType::Sword;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Weapon")
	float AttackRange = 200.0f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Weapon")
	float AttackSpeed = 1.0f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Weapon")
	float BaseDamage = 15.0f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Weapon")
	EDamageType DamageType = EDamageType::Slash;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Weapon")
	EInnocentDevilType EvoCrystalColor = EInnocentDevilType::None;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Weapon")
	TArray<FAnimMontage> ComboAnimations;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Weapon")
	TArray<FAnimMontage> FinalAttackAnimations;
};

USTRUCT(BlueprintType)
struct FWeaponRecipe
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Crafting")
	FName WeaponName;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Crafting")
	TArray<FName> RequiredMaterials;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Crafting")
	EWeaponType WeaponType = EWeaponType::Sword;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Crafting")
	EDamageType DamageType = EDamageType::Slash;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Crafting")
	int32 ForgeLevel = 1;
};

USTRUCT(BlueprintType)
struct FMaterialData
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Materials")
	FName MaterialName;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Materials")
	FLinearColor MaterialColor = FLinearColor::White;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Materials")
	bool bIsRare = false;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Materials")
	FText Description;
};

USTRUCT(BlueprintType)
struct FInnocentDevilData
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Innocent Devil")
	FName DevilName;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Innocent Devil")
	EInnocentDevilType DevilType = EInnocentDevilType::Fairy;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Innocent Devil")
	int32 Level = 1;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Innocent Devil")
	int32 Experience = 0;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Innocent Devil")
	int32 Health = 100;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Innocent Devil")
	int32 MaxHealth = 100;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Innocent Devil")
	int32 Attack = 10;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Innocent Devil")
	bool bIsUnlocked = false;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Innocent Devil")
	bool bIsEvolved = false;
};

USTRUCT(BlueprintType)
struct FInventoryItem
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Inventory")
	FName ItemName;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Inventory")
	int32 Quantity = 1;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Inventory")
	bool bIsEquipped = false;
};

//=============================================================================
// ENEMY DATA
//=============================================================================

USTRUCT(BlueprintType)
struct FEnemyData
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Enemy")
	FName EnemyName;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Enemy")
	int32 Chapter = 1;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Enemy")
	float Health = 50.0f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Enemy")
	float Damage = 10.0f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Enemy")
	float AttackRange = 150.0f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Enemy")
	float DetectionRange = 600.0f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Enemy")
	FString Weaknesses; // Comma-separated damage type names

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Enemy")
	FString Tolerances; // Comma-separated damage type names

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Enemy")
	FString ItemDrops; // Comma-separated item names

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Enemy")
	bool CanBeStolen = false;
};

//=============================================================================
// ENEMY ENCOUNTER
//=============================================================================

USTRUCT(BlueprintType)
struct FEnemyEncounter
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Encounter")
	int32 Chapter = 1;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Encounter")
	FName EnemyName;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Encounter")
	int32 Count = 1;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Encounter")
	FName SpawnLocation;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Encounter")
	float RespawnTime = 0.0f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Encounter")
	bool IsBoss = false;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Encounter")
	bool Stealable = false;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Encounter")
	FName StealItem;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Encounter")
	FString Weakness; // Damage type name

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Encounter")
	FString Tolerance; // Damage type name

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Encounter")
	float Health = 50.0f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Encounter")
	float Damage = 10.0f;
};

//=============================================================================
// ITEM DROP
//=============================================================================

USTRUCT(BlueprintType)
struct FItemDrop
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "ItemDrop")
	FName EnemyName;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "ItemDrop")
	FName ItemName;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "ItemDrop")
	float DropChance = 0.0f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "ItemDrop")
	bool IsStealOnly = false;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "ItemDrop")
	bool IsRare = false;
};

//=============================================================================
// WEAPON MATERIAL REQUIREMENT
//=============================================================================

USTRUCT(BlueprintType)
struct FWeaponMaterialRequirement
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "WeaponMaterial")
	FName WeaponName;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "WeaponMaterial")
	FName Material1;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "WeaponMaterial")
	FName Material2;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "WeaponMaterial")
	FName Material3;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "WeaponMaterial")
	FName Material4;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "WeaponMaterial")
	int32 Material1Count = 0;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "WeaponMaterial")
	int32 Material2Count = 0;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "WeaponMaterial")
	int32 Material3Count = 0;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "WeaponMaterial")
	int32 Material4Count = 0;
};

//=============================================================================
// INNOCENT DEVIL EVOLUTION
//=============================================================================

USTRUCT(BlueprintType)
struct FInnocentDevilEvolution
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Innocent Devil")
	FName DevilName;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Innocent Devil")
	EInnocentDevilType DevilType = EInnocentDevilType::Fairy;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Innocent Devil")
	int32 Level = 1;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Innocent Devil")
	FName BaseForm;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Innocent Devil")
	FName EvolvedForm;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Innocent Devil")
	FName FinalForm;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Innocent Devil")
	FName EvoCrystalRequired;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Innocent Devil")
	int32 EvoCrystalCount = 0;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Innocent Devil")
	FString AbilityUnlock;
};

//=============================================================================
// CHAPTER PROGRESSION
//=============================================================================

USTRUCT(BlueprintType)
struct FChapterProgression
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Chapter")
	int32 Chapter = 1;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Chapter")
	FName ChapterName;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Chapter")
	FString UnlockRequirement;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Chapter")
	TArray<FName> SaveRooms;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Chapter")
	TArray<FName> GreenDoorRooms;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Chapter")
	EInnocentDevilType InnocentDevilAcquired = EInnocentDevilType::None;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Chapter")
	FName WeaponUnlocked;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Chapter")
	FString AreaType;
};

//=============================================================================
// TIMING CONSTANTS
//=============================================================================

constexpr float PERFECT_GUARD_WINDOW = 0.1f;   // Release guard within 0.1s before impact
constexpr float QUICK_STEP_IFRAMES = 0.3f;     // Invulnerability duration
constexpr float DOUBLE_STEP_WINDOW = 0.5f;     // Max time between two quick steps
constexpr float COMBO_STAGE_1_WINDOW = 0.35f;
constexpr float COMBO_STAGE_2_WINDOW = 0.45f;
constexpr float COMBO_STAGE_3_WINDOW = 0.60f;