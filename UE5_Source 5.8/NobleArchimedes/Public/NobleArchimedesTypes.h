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
// TIMING CONSTANTS
//=============================================================================

constexpr float PERFECT_GUARD_WINDOW = 0.1f;   // Release guard within 0.1s before impact
constexpr float QUICK_STEP_IFRAMES = 0.3f;     // Invulnerability duration
constexpr float DOUBLE_STEP_WINDOW = 0.5f;     // Max time between two quick steps
constexpr float COMBO_STAGE_1_WINDOW = 0.35f;
constexpr float COMBO_STAGE_2_WINDOW = 0.45f;
constexpr float COMBO_STAGE_3_WINDOW = 0.60f;