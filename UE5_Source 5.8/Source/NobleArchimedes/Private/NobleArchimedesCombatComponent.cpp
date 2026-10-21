// Fill out your copyright notice in the Description page of Project Settings.

#include "NobleArchimedesCombatComponent.h"
#include "HectorCharacter.h"
#include "EnemyBase.h"
#include "CandleBreakable.h"
#include "Engine/DataTable.h"
#include "Engine/EngineTypes.h"
#include "Engine/World.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "Kismet/KismetSystemLibrary.h"
#include "TimerManager.h"

UNobleArchimedesCombatComponent::UNobleArchimedesCombatComponent()
{
	PrimaryComponentTick.bCanEverTick = true;
}

void UNobleArchimedesCombatComponent::BeginPlay()
{
	Super::BeginPlay();

	CurrentHealth = MaxHealth;
	Mana = MaxMana;
	LoadWeaponData();
}

void UNobleArchimedesCombatComponent::LoadWeaponData()
{
	WeaponDataByName.Empty();
	WeaponDataTable.Empty();

	if (WeaponDataTableAsset)
	{
		TArray<FWeaponData*> Rows;
		WeaponDataTableAsset->GetAllRows<FWeaponData>(TEXT("Combat"), Rows);
		for (const FWeaponData* Row : Rows)
		{
			if (!Row || Row->WeaponName.IsNone())
			{
				continue;
			}

			WeaponDataByName.Add(Row->WeaponName, *Row);

			// Keep the strongest weapon of each type as the default for that
			// type; exact forged weapons are equipped by name.
			FWeaponData& Existing = WeaponDataTable.FindOrAdd(Row->WeaponType);
			if (Existing.WeaponName.IsNone() || Row->BaseDamage > Existing.BaseDamage)
			{
				Existing = *Row;
			}
		}
	}

	// Safe fallback so the character is playable before the DataTable is
	// assigned (e.g. in a bare C++ test map).
	if (WeaponDataByName.Num() == 0)
	{
		FWeaponData SwordData;
		SwordData.WeaponName = "Short Sword";
		SwordData.WeaponType = EWeaponType::Sword;
		SwordData.AttackRange = 200.0f;
		SwordData.AttackSpeed = 1.0f;
		SwordData.BaseDamage = 15.0f;
		SwordData.DamageType = EDamageType::Slash;
		SwordData.EvoCrystalColor = EEvolutionCrystalType::Light;
		WeaponDataByName.Add(SwordData.WeaponName, SwordData);
		WeaponDataTable.Add(EWeaponType::Sword, SwordData);

		FWeaponData AxeData;
		AxeData.WeaponName = "Battle Axe";
		AxeData.WeaponType = EWeaponType::Axe;
		AxeData.AttackRange = 180.0f;
		AxeData.AttackSpeed = 0.7f;
		AxeData.BaseDamage = 25.0f;
		AxeData.DamageType = EDamageType::Blunt;
		AxeData.EvoCrystalColor = EEvolutionCrystalType::Dark;
		WeaponDataByName.Add(AxeData.WeaponName, AxeData);
		WeaponDataTable.Add(EWeaponType::Axe, AxeData);

		FWeaponData SpearData;
		SpearData.WeaponName = "Long Spear";
		SpearData.WeaponType = EWeaponType::Spear;
		SpearData.AttackRange = 350.0f;
		SpearData.AttackSpeed = 0.8f;
		SpearData.BaseDamage = 18.0f;
		SpearData.DamageType = EDamageType::Slash;
		SpearData.EvoCrystalColor = EEvolutionCrystalType::Fire;
		WeaponDataByName.Add(SpearData.WeaponName, SpearData);
		WeaponDataTable.Add(EWeaponType::Spear, SpearData);

		FWeaponData KnucklesData;
		KnucklesData.WeaponName = "Punch Rings";
		KnucklesData.WeaponType = EWeaponType::Knuckles;
		KnucklesData.AttackRange = 100.0f;
		KnucklesData.AttackSpeed = 1.3f;
		KnucklesData.BaseDamage = 12.0f;
		KnucklesData.DamageType = EDamageType::Blunt;
		KnucklesData.EvoCrystalColor = EEvolutionCrystalType::Ice;
		WeaponDataByName.Add(KnucklesData.WeaponName, KnucklesData);
		WeaponDataTable.Add(EWeaponType::Knuckles, KnucklesData);

		FWeaponData SpecialData;
		SpecialData.WeaponName = "Shuriken";
		SpecialData.WeaponType = EWeaponType::Special;
		SpecialData.AttackRange = 400.0f;
		SpecialData.AttackSpeed = 0.5f;
		SpecialData.BaseDamage = 10.0f;
		SpecialData.DamageType = EDamageType::Magic;
		SpecialData.EvoCrystalColor = EEvolutionCrystalType::None;
		WeaponDataByName.Add(SpecialData.WeaponName, SpecialData);
		WeaponDataTable.Add(EWeaponType::Special, SpecialData);
	}

	if (const FWeaponData* DefaultData = WeaponDataByName.Find(DefaultWeaponName))
	{
		CurrentWeaponData = *DefaultData;
		CurrentWeaponType = DefaultData->WeaponType;
	}
	else if (const FWeaponData* TypeData = WeaponDataTable.Find(CurrentWeaponType))
	{
		CurrentWeaponData = *TypeData;
	}
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

	// Schedule the actual weapon hit on the swing's active frame, derived from
	// the montage so each attack connects at its own point.
	FTimerDelegate HitDelegate = FTimerDelegate::CreateUObject(
		this, &UNobleArchimedesCombatComponent::ApplyAttackHit, CurrentComboStage, false);
	GetWorld()->GetTimerManager().SetTimer(AttackHitTimer, HitDelegate,
		GetAttackHitDelay(CurrentComboStage, false), false);
	GetWorld()->GetTimerManager().SetTimer(
		AttackStateTimer, this, &UNobleArchimedesCombatComponent::EndAttack, GetAttackDuration(), false);

	// Set combo window for next attack
	GetWorld()->GetTimerManager().SetTimer(ComboResetTimer, this, &UNobleArchimedesCombatComponent::ResetCombo,
		CurrentComboStage == 1 ? COMBO_STAGE_1_WINDOW :
		CurrentComboStage == 2 ? COMBO_STAGE_2_WINDOW : COMBO_STAGE_3_WINDOW, false);
}

void UNobleArchimedesCombatComponent::HeavyAttack()
{
	if (bIsAttacking || bIsInvulnerable) return;

	bIsAttacking = true;
	const int32 FinisherStage = FMath::Max(1, CurrentComboStage);
	PlayFinalAttackMontage(FinisherStage);

	FTimerDelegate HitDelegate = FTimerDelegate::CreateUObject(
		this, &UNobleArchimedesCombatComponent::ApplyAttackHit, FinisherStage, true);
	GetWorld()->GetTimerManager().SetTimer(AttackHitTimer, HitDelegate,
		GetAttackHitDelay(FinisherStage, true), false);
	GetWorld()->GetTimerManager().SetTimer(
		AttackStateTimer, this, &UNobleArchimedesCombatComponent::EndAttack, GetAttackDuration(), false);

	ResetCombo();
}

void UNobleArchimedesCombatComponent::ResetCombo()
{
	CurrentComboStage = 0;
	bComboWindowOpen = false;
	GetWorld()->GetTimerManager().ClearTimer(ComboResetTimer);
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
		const float GuardDuration = GetWorld() ? (GetWorld()->GetTimeSeconds() - GuardStartTime) : 1.0f;
		if (GuardDuration <= PerfectGuardWindow)
		{
			FinalDamage = 0.0f; // Perfect guard: timed guard start blocks everything
			bPerfectGuard = true;
		}
		else
		{
			FinalDamage *= 0.3f; // 70% damage reduction while guarding
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
		if (AHectorCharacter* Char = Cast<AHectorCharacter>(GetOwner()))
		{
			Char->HandleDeath();
		}
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
	if (const FWeaponData* Data = WeaponDataTable.Find(NewWeaponType))
	{
		CurrentWeaponData = *Data;
	}
}

bool UNobleArchimedesCombatComponent::EquipWeaponByName(FName WeaponName)
{
	const FWeaponData* Data = WeaponDataByName.Find(WeaponName);
	if (!Data)
	{
		return false;
	}

	CurrentWeaponData = *Data;
	CurrentWeaponType = Data->WeaponType;
	return true;
}

FWeaponData UNobleArchimedesCombatComponent::GetWeaponDataByName(FName WeaponName) const
{
	if (const FWeaponData* Data = WeaponDataByName.Find(WeaponName))
	{
		return *Data;
	}
	return FWeaponData();
}

TArray<FName> UNobleArchimedesCombatComponent::GetKnownWeaponNames() const
{
	TArray<FName> Names;
	WeaponDataByName.GetKeys(Names);
	Names.Sort([](const FName& A, const FName& B)
	{
		return A.ToString() < B.ToString();
	});
	return Names;
}

float UNobleArchimedesCombatComponent::GetAttackDuration() const
{
	const float Speed = FMath::Max(0.1f, CurrentWeaponData.AttackSpeed);
	return FMath::Clamp(0.45f / Speed, 0.18f, 1.2f);
}

void UNobleArchimedesCombatComponent::EndAttack()
{
	bIsAttacking = false;
}

void UNobleArchimedesCombatComponent::ApplyAttackHit(int32 ComboStage, bool bHeavyAttack)
{
	UWorld* World = GetWorld();
	AHectorCharacter* Char = Cast<AHectorCharacter>(GetOwner());
	if (!World || !Char)
	{
		return;
	}

	// Aim along the camera, not the actor. With bOrientRotationToMovement the
	// actor only turns while moving, so attacking from a standstill used to swing
	// at whatever direction Hector happened to be facing and miss everything in
	// front of the player. GetBaseAimRotation() returns the control rotation for
	// a player-controlled pawn and falls back to actor rotation for AI.
	const FRotator AimRotation = Char->GetBaseAimRotation();
	const FVector Forward = FRotationMatrix(
		FRotator(0.0f, AimRotation.Yaw, 0.0f)).GetUnitAxis(EAxis::X);
	const FVector Start = Char->GetActorLocation() + FVector(0.0f, 0.0f, 40.0f)
		+ Forward * AttackTraceForwardOffset;
	const FVector End = Start + Forward * FMath::Max(60.0f, CurrentWeaponData.AttackRange);

	TArray<FHitResult> Hits;
	TArray<AActor*> IgnoreActors;
	IgnoreActors.Add(Char);

	UKismetSystemLibrary::SphereTraceMulti(
		World,
		Start,
		End,
		AttackTraceRadius,
		UEngineTypes::ConvertToTraceType(ECC_Pawn),
		false,
		IgnoreActors,
		EDrawDebugTrace::None,
		Hits,
		true);

	TSet<AActor*> HitActors;
	const float ComboMultiplier = bHeavyAttack
		? 1.8f
		: (1.0f + 0.15f * FMath::Max(0, ComboStage - 1));
	const float Damage = CurrentWeaponData.BaseDamage * ComboMultiplier;

	for (const FHitResult& Hit : Hits)
	{
		AActor* HitActor = Hit.GetActor();
		if (!HitActor || HitActors.Contains(HitActor))
		{
			continue;
		}

		if (AEnemyBase* Enemy = Cast<AEnemyBase>(HitActor))
		{
			HitActors.Add(HitActor);
			Enemy->ApplyDamage(Damage, CurrentWeaponData.DamageType);
			Enemy->LaunchCharacter(Forward * 200.0f + FVector(0.0f, 0.0f, 120.0f), false, false);
			UE_LOG(LogTemp, Log, TEXT("NobleArchimedes: %s hit %s for %.1f (%s)."),
				*CurrentWeaponData.WeaponName.ToString(), *Enemy->GetName(), Damage,
				*StaticEnum<EDamageType>()->GetNameStringByValue(static_cast<int64>(CurrentWeaponData.DamageType)));
		}
		else if (ACandleBreakable* Candle = Cast<ACandleBreakable>(HitActor))
		{
			HitActors.Add(HitActor);
			Candle->BreakCandle();
		}
	}
}

float UNobleArchimedesCombatComponent::GetAttackHitDelay(int32 Stage, bool bHeavyAttack) const
{
	const TArray<UAnimMontage*>& Montages = bHeavyAttack
		? CurrentWeaponData.FinalAttackAnimations
		: CurrentWeaponData.ComboAnimations;

	const int32 Index = FMath::Max(0, Stage - 1);
	if (Montages.IsValidIndex(Index) && Montages[Index])
	{
		const float Length = Montages[Index]->GetPlayLength();
		if (Length > 0.0f)
		{
			// Hit lands on the first active frame, about a third into the clip.
			const float Delay = FMath::Clamp(Length * AttackHitFraction, 0.02f, 0.6f);
			UE_LOG(LogTemp, Log,
				TEXT("NA-ANIM: %s stage %d hit at %.3fs (clip %.2fs)."),
				bHeavyAttack ? TEXT("finisher") : TEXT("combo"), Stage, Delay, Length);
			return Delay;
		}
	}

	// No montage for this stage: fall back to the authored delay so the attack
	// still resolves instead of hitting instantly.
	return AttackHitDelay;
}

float UNobleArchimedesCombatComponent::GetComboWindowSeconds(int32 Stage) const
{
	switch (Stage)
	{
	case 2:
		return COMBO_STAGE_2_WINDOW;
	case 3:
		return COMBO_STAGE_3_WINDOW;
	default:
		return COMBO_STAGE_1_WINDOW;
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
	// Called by an enemy immediately before its hit lands. A guard started
	// inside the 0.1s window is a perfect guard.
	if (!bIsGuarding || !GetWorld())
	{
		bPerfectGuard = false;
		return;
	}

	const float GuardDuration = GetWorld()->GetTimeSeconds() - GuardStartTime;
	bPerfectGuard = (GuardDuration <= PerfectGuardWindow);
}

void UNobleArchimedesCombatComponent::ApplyDamageReduction(float& Damage, EDamageType DamageType)
{
	// Weakness/tolerance logic
	// Fire <-> Ice, Light <-> Dark
	if ((DamageType == EDamageType::Fire && CurrentWeaponData.EvoCrystalColor == EEvolutionCrystalType::Ice) ||
		(DamageType == EDamageType::Ice && CurrentWeaponData.EvoCrystalColor == EEvolutionCrystalType::Fire) ||
		(DamageType == EDamageType::Light && CurrentWeaponData.EvoCrystalColor == EEvolutionCrystalType::Dark) ||
		(DamageType == EDamageType::Dark && CurrentWeaponData.EvoCrystalColor == EEvolutionCrystalType::Light))
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
			UAnimMontage* Montage = CurrentWeaponData.ComboAnimations[Stage - 1];
			if (Montage)
			{
				Char->PlayAnimMontage(Montage);
				UE_LOG(LogTemp, Log, TEXT("NA-ANIM: combo stage %d -> %s."),
					Stage, *Montage->GetName());
			}
			else
			{
				UE_LOG(LogTemp, Warning,
					TEXT("NA-ANIM: %s has no combo montage for stage %d."),
					*CurrentWeaponData.WeaponName.ToString(), Stage);
			}
		}
	}
}

void UNobleArchimedesCombatComponent::PlayFinalAttackMontage(int32 Stage)
{
	if (AHectorCharacter* Char = Cast<AHectorCharacter>(GetOwner()))
	{
		if (CurrentWeaponData.FinalAttackAnimations.IsValidIndex(Stage - 1))
		{
			UAnimMontage* Montage = CurrentWeaponData.FinalAttackAnimations[Stage - 1];
			if (Montage)
			{
				Char->PlayAnimMontage(Montage);
				UE_LOG(LogTemp, Log, TEXT("NA-ANIM: finisher stage %d -> %s."),
					Stage, *Montage->GetName());
			}
			else
			{
				UE_LOG(LogTemp, Warning,
					TEXT("NA-ANIM: %s has no finisher montage for stage %d."),
					*CurrentWeaponData.WeaponName.ToString(), Stage);
			}
		}
	}
}