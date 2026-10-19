// Fill out your copyright notice in the Description page of Project Settings.

#include "NobleArchimedesCombatComponent.h"
#include "NobleArchimedesCharacter.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "Kismet/KismetSystemLibrary.h"

UNobleArchimedesCombatComponent::UNobleArchimedesCombatComponent()
{
	PrimaryComponentTick.bCanEverTick = true;
}

void UNobleArchimedesCombatComponent::BeginPlay()
{
	Super::BeginPlay();

	CurrentHealth = MaxHealth;

	// Initialize default weapon data
	FWeaponData SwordData;
	SwordData.WeaponName = "Short Sword";
	SwordData.WeaponType = EWeaponType::Sword;
	SwordData.AttackRange = 200.0f;
	SwordData.AttackSpeed = 1.0f;
	SwordData.BaseDamage = 15.0f;
	SwordData.DamageType = EDamageType::Slash;
	WeaponDataTable.Add(EWeaponType::Sword, SwordData);

	FWeaponData AxeData;
	AxeData.WeaponName = "Battle Axe";
	AxeData.WeaponType = EWeaponType::Axe;
	AxeData.AttackRange = 180.0f;
	AxeData.AttackSpeed = 0.7f;
	AxeData.BaseDamage = 25.0f;
	AxeData.DamageType = EDamageType::Blunt;
	WeaponDataTable.Add(EWeaponType::Axe, AxeData);

	FWeaponData SpearData;
	SpearData.WeaponName = "Long Spear";
	SpearData.WeaponType = EWeaponType::Spear;
	SpearData.AttackRange = 350.0f;
	SpearData.AttackSpeed = 0.8f;
	SpearData.BaseDamage = 18.0f;
	SpearData.DamageType = EDamageType::Slash;
	WeaponDataTable.Add(EWeaponType::Spear, SpearData);

	FWeaponData KnucklesData;
	KnucklesData.WeaponName = "Punch Rings";
	KnucklesData.WeaponType = EWeaponType::Knuckles;
	KnucklesData.AttackRange = 100.0f;
	KnucklesData.AttackSpeed = 1.3f;
	KnucklesData.BaseDamage = 12.0f;
	KnucklesData.DamageType = EDamageType::Blunt;
	WeaponDataTable.Add(EWeaponType::Knuckles, KnucklesData);

	CurrentWeaponData = SwordData;
}

void UNobleArchimedesCombatComponent::TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction)
{
	Super::TickComponent(DeltaTime, TickType, ThisTickFunction);

	UpdateCombo(DeltaTime);
	UpdateInvulnerability(DeltaTime);
	UpdateDoubleStep(DeltaTime);
}

void UNobleArchimedesCombatComponent::LightAttack()
{
	if (bIsAttacking || bIsInvulnerable) return;

	bIsAttacking = true;
	CurrentComboStage++;

	if (CurrentComboStage > 3)
	{
		CurrentComboStage = 1;
	}

	PlayAttackMontage(CurrentComboStage);

	// Set combo window for next attack
	GetWorldTimerManager().SetTimer(ComboResetTimer, this, &UNobleArchimedesCombatComponent::ResetCombo, 
		CurrentComboStage == 1 ? COMBO_STAGE_1_WINDOW :
		CurrentComboStage == 2 ? COMBO_STAGE_2_WINDOW : COMBO_STAGE_3_WINDOW, false);
}

void UNobleArchimedesCombatComponent::HeavyAttack()
{
	if (bIsAttacking || bIsInvulnerable) return;

	bIsAttacking = true;
	PlayFinalAttackMontage(CurrentComboStage);

	ResetCombo();
}

void UNobleArchimedesCombatComponent::ResetCombo()
{
	CurrentComboStage = 0;
	bComboWindowOpen = false;
	GetWorldTimerManager().ClearTimer(ComboResetTimer);
}

void UNobleArchimedesCombatComponent::StartGuard()
{
	if (bIsAttacking || bIsInvulnerable) return;

	bIsGuarding = true;
	bPerfectGuard = false;
	GuardStartTime = GetWorld()->GetTimeSeconds();
}

void UNobleArchimedesCombatComponent::EndGuard()
{
	if (!bIsGuarding) return;

	float GuardDuration = GetWorld()->GetTimeSeconds() - GuardStartTime;

	// Check perfect guard: release within window before enemy impact
	// The actual impact check is done by the enemy attack system
	// For now, mark as potential perfect guard if released quickly
	if (GuardDuration <= PerfectGuardWindow)
	{
		bPerfectGuard = true;
	}

	bIsGuarding = false;
}

void UNobleArchimedesCombatComponent::QuickStep(FVector Direction)
{
	if (bIsAttacking || bIsInvulnerable) return;

	bIsInvulnerable = true;
	InvulnerabilityTimer = QuickStepIframes;

	// Check double step
	float TimeSinceLastStep = GetWorld()->GetTimeSeconds() - LastQuickStepTime;
	if (TimeSinceLastStep <= DoubleStepWindow)
	{
		bCanDoubleStep = true;
	}
	else
	{
		bCanDoubleStep = false;
	}

	LastQuickStepTime = GetWorld()->GetTimeSeconds();

	// Apply movement
	if (ANobleArchimedesCharacter* Char = Cast<ANobleArchimedesCharacter>(GetOwner()))
	{
		FVector LaunchDir = Direction;
		LaunchDir.Z = 0.0f;
		LaunchDir.Normalize();
		Char->LaunchCharacter(LaunchDir * 800.0f, false, false);
	}
}

void UNobleArchimedesCombatComponent::TakeDamage(float DamageAmount, EDamageType DamageType)
{
	if (bIsInvulnerable) return;

	float FinalDamage = DamageAmount;
	ApplyDamageReduction(FinalDamage, DamageType);

	if (bIsGuarding)
	{
		FinalDamage *= 0.3f; // 70% damage reduction when guarding
		if (bPerfectGuard)
		{
			FinalDamage = 0.0f; // Perfect guard blocks all damage
			bPerfectGuard = false;
		}
	}

	CurrentHealth = FMath::Max(0.0f, CurrentHealth - FinalDamage);

	if (CurrentHealth <= 0.0f)
	{
		// Death handled by character
	}
}

void UNobleArchimedesCombatComponent::SetHealth(float NewHealth)
{
	CurrentHealth = FMath::Clamp(NewHealth, 0.0f, MaxHealth);
}

void UNobleArchimedesCombatComponent::EquipWeapon(EWeaponType NewWeaponType)
{
	CurrentWeaponType = NewWeaponType;
	if (WeaponDataTable.Contains(NewWeaponType))
	{
		CurrentWeaponData = WeaponDataTable[NewWeaponType];
	}
}

void UNobleArchimedesCombatComponent::UpdateCombo(float DeltaTime)
{
	if (bComboWindowOpen)
	{
		ComboTimer += DeltaTime;
	}
}

void UNobleArchimedesCombatComponent::UpdateInvulnerability(float DeltaTime)
{
	if (bIsInvulnerable)
	{
		InvulnerabilityTimer -= DeltaTime;
		if (InvulnerabilityTimer <= 0.0f)
		{
			bIsInvulnerable = false;
		}
	}
}

void UNobleArchimedesCombatComponent::UpdateDoubleStep(float DeltaTime)
{
	if (bCanDoubleStep)
	{
		DoubleStepTimer += DeltaTime;
		if (DoubleStepTimer > DoubleStepWindow)
		{
			bCanDoubleStep = false;
			DoubleStepTimer = 0.0f;
		}
	}
}

void UNobleArchimedesCombatComponent::CheckPerfectGuard()
{
	// Called by enemy attack system when attack connects
	// If guard is active and release was within window, trigger perfect guard
}

void UNobleArchimedesCombatComponent::ApplyDamageReduction(float& Damage, EDamageType DamageType)
{
	// Weakness/tolerance logic
	// Fire <-> Ice, Light <-> Dark
	if ((DamageType == EDamageType::Fire && CurrentWeaponData.DamageType == EDamageType::Ice) ||
		(DamageType == EDamageType::Ice && CurrentWeaponData.DamageType == EDamageType::Fire) ||
		(DamageType == EDamageType::Light && CurrentWeaponData.DamageType == EDamageType::Dark) ||
		(DamageType == EDamageType::Dark && CurrentWeaponData.DamageType == EDamageType::Light))
	{
		Damage *= 1.5f; // Weakness bonus
	}
}

void UNobleArchimedesCombatComponent::PlayAttackMontage(int32 Stage)
{
	if (ANobleArchimedesCharacter* Char = Cast<ANobleArchimedesCharacter>(GetOwner()))
	{
		if (CurrentWeaponData.ComboAnimations.IsValidIndex(Stage - 1))
		{
			Char->PlayAnimMontage(CurrentWeaponData.ComboAnimations[Stage - 1]);
		}
	}
}

void UNobleArchimedesCombatComponent::PlayFinalAttackMontage(int32 Stage)
{
	if (ANobleArchimedesCharacter* Char = Cast<ANobleArchimedesCharacter>(GetOwner()))
	{
		if (CurrentWeaponData.FinalAttackAnimations.IsValidIndex(Stage - 1))
		{
			Char->PlayAnimMontage(CurrentWeaponData.FinalAttackAnimations[Stage - 1]);
		}
	}
}