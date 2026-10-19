// Fill out your copyright notice in the Description page of Project Settings.

#include "NobleArchimedesCombatComponent.h"
#include "HectorCharacter.h"
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
	Mana = MaxMana;

	// Initialize default weapon data
	FWeaponData SwordData;
	SwordData.WeaponName = "Short Sword";
	SwordData.WeaponType = EWeaponType::Sword;
	SwordData.AttackRange = 200.0f;
	SwordData.AttackSpeed = 1.0f;
	SwordData.BaseDamage = 15.0f;
	SwordData.DamageType = EDamageType::Slash;
	SwordData.EvoCrystalColor = EInnocentDevilType::Light;
	WeaponDataTable.Add(EWeaponType::Sword, SwordData);

	FWeaponData AxeData;
	AxeData.WeaponName = "Battle Axe";
	AxeData.WeaponType = EWeaponType::Axe;
	AxeData.AttackRange = 180.0f;
	AxeData.AttackSpeed = 0.7f;
	AxeData.BaseDamage = 25.0f;
	AxeData.DamageType = EDamageType::Blunt;
	AxeData.EvoCrystalColor = EInnocentDevilType::Dark;
	WeaponDataTable.Add(EWeaponType::Axe, AxeData);

	FWeaponData SpearData;
	SpearData.WeaponName = "Long Spear";
	SpearData.WeaponType = EWeaponType::Spear;
	SpearData.AttackRange = 350.0f;
	SpearData.AttackSpeed = 0.8f;
	SpearData.BaseDamage = 18.0f;
	SpearData.DamageType = EDamageType::Slash;
	SpearData.EvoCrystalColor = EInnocentDevilType::Fire;
	WeaponDataTable.Add(EWeaponType::Spear, SpearData);

	FWeaponData KnucklesData;
	KnucklesData.WeaponName = "Punch Rings";
	KnucklesData.WeaponType = EWeaponType::Knuckles;
	KnucklesData.AttackRange = 100.0f;
	KnucklesData.AttackSpeed = 1.3f;
	KnucklesData.BaseDamage = 12.0f;
	KnucklesData.DamageType = EDamageType::Blunt;
	KnucklesData.EvoCrystalColor = EInnocentDevilType::Ice;
	WeaponDataTable.Add(EWeaponType::Knuckles, KnucklesData);

	FWeaponData SpecialData;
	SpecialData.WeaponName = "Shuriken";
	SpecialData.WeaponType = EWeaponType::Special;
	SpecialData.AttackRange = 400.0f;
	SpecialData.AttackSpeed = 0.5f;
	SpecialData.BaseDamage = 10.0f;
	SpecialData.DamageType = EDamageType::Magic;
	SpecialData.EvoCrystalColor = EInnocentDevilType::None;
	WeaponDataTable.Add(EWeaponType::Special, SpecialData);

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

	// After Light Attack 3, the only options are Heavy Attack or return to Idle.
	// Do not allow Light Attack to loop back to Light 1.
	if (CurrentComboStage >= 3)
	{
		return;
	}

	bIsAttacking = true;
	CurrentComboStage++;

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

	bIsGuarding = false;
	bPerfectGuard = false;

	// Record when guard was released. Perfect guard is determined later by
	// CheckPerfectGuard() when an enemy attack connects: the player must have
	// released guard within PerfectGuardWindow (0.1s) before the impact.
	LastGuardReleaseTime = GetWorld()->GetTimeSeconds();
	bWasRecentlyGuarding = true;
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
	if (AHectorCharacter* Char = Cast<AHectorCharacter>(GetOwner()))
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

	// Death Doll activation - Hector dies instead of player
	if (CurrentHealth <= 0.0f && bHasDeathDoll)
	{
		CurrentHealth = MaxHealth * 0.5f; // Revive at half health
		bHasDeathDoll = false;
		// Death Doll is consumed
		return;
	}

	if (CurrentHealth <= 0.0f)
	{
		// Death handled by character
	}
}

void UNobleArchimedesCombatComponent::SetHealth(float NewHealth)
{
	CurrentHealth = FMath::Clamp(NewHealth, 0.0f, MaxHealth);
}

void UNobleArchimedesCombatComponent::SetMaxHealth(float NewMaxHealth)
{
	MaxHealth = FMath::Max(0.0f, NewMaxHealth);
	CurrentHealth = FMath::Clamp(CurrentHealth, 0.0f, MaxHealth);
}

void UNobleArchimedesCombatComponent::SetMana(float NewMana)
{
	Mana = FMath::Clamp(NewMana, 0.0f, MaxMana);
}

void UNobleArchimedesCombatComponent::SetMaxMana(float NewMaxMana)
{
	MaxMana = FMath::Max(0.0f, NewMaxMana);
	Mana = FMath::Clamp(Mana, 0.0f, MaxMana);
}

void UNobleArchimedesCombatComponent::ApplyDeathDoll()
{
	// Death Doll consumed on next death instead of game over
}

void UNobleArchimedesCombatComponent::SetDeathDoll(bool bHas)
{
	bHasDeathDoll = bHas;
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
	// Called by enemy attack system when attack connects.
	// Perfect Guard: player released guard within PerfectGuardWindow (0.1s) before this moment.
	if (bWasRecentlyGuarding)
	{
		float TimeSinceRelease = GetWorld()->GetTimeSeconds() - LastGuardReleaseTime;
		if (TimeSinceRelease <= PerfectGuardWindow)
		{
			bPerfectGuard = true;
		}
		bWasRecentlyGuarding = false;
	}
}

void UNobleArchimedesCombatComponent::ApplyDamageReduction(float& Damage, EDamageType DamageType)
{
	// Weakness/tolerance logic
	// Fire <-> Ice, Light <-> Dark
	if ((DamageType == EDamageType::Fire && CurrentWeaponData.EvoCrystalColor == EInnocentDevilType::Ice) ||
		(DamageType == EDamageType::Ice && CurrentWeaponData.EvoCrystalColor == EInnocentDevilType::Fire) ||
		(DamageType == EDamageType::Light && CurrentWeaponData.EvoCrystalColor == EInnocentDevilType::Dark) ||
		(DamageType == EDamageType::Dark && CurrentWeaponData.EvoCrystalColor == EInnocentDevilType::Light))
	{
		Damage *= 1.5f; // Weakness bonus
	}
}

void UNobleArchimedesCombatComponent::PlayAttackMontage(int32 Stage)
{
	if (AHectorCharacter* Char = Cast<AHectorCharacter>(GetOwner()))
	{
		if (CurrentWeaponData.ComboAnimations.IsValidIndex(Stage - 1))
		{
			Char->PlayAnimMontage(CurrentWeaponData.ComboAnimations[Stage - 1]);
		}
	}
}

void UNobleArchimedesCombatComponent::PlayFinalAttackMontage(int32 Stage)
{
	if (AHectorCharacter* Char = Cast<AHectorCharacter>(GetOwner()))
	{
		if (CurrentWeaponData.FinalAttackAnimations.IsValidIndex(Stage - 1))
		{
			Char->PlayAnimMontage(CurrentWeaponData.FinalAttackAnimations[Stage - 1]);
		}
	}
}