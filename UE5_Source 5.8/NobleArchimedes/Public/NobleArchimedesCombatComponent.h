// Fill out your copyright notice in the Description page of Project Settings.

#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "TimerManager.h"
#include "NobleArchimedesTypes.h"
#include "NobleArchimedesCombatComponent.generated.h"

class AHectorCharacter;
class AEnemyBase;
class UDataTable;

UCLASS(ClassGroup = (Custom), meta = (BlueprintSpawnableComponent))
class NOBLEARCHIMEDES_API UNobleArchimedesCombatComponent : public UActorComponent
{
	GENERATED_BODY()

public:
	UNobleArchimedesCombatComponent();

	virtual void BeginPlay() override;
	virtual void TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction) override;

	//=============================================================================
	// ATTACK SYSTEM
	//=============================================================================

	UFUNCTION(BlueprintCallable, Category = "Combat")
	void LightAttack();

	UFUNCTION(BlueprintCallable, Category = "Combat")
	void HeavyAttack();

	UFUNCTION(BlueprintCallable, Category = "Combat")
	void ResetCombo();

	UFUNCTION(BlueprintCallable, BlueprintPure, Category = "Combat")
	int32 GetCurrentComboStage() const { return CurrentComboStage; }

	UFUNCTION(BlueprintCallable, BlueprintPure, Category = "Combat")
	bool IsAttacking() const { return bIsAttacking; }

	/**
	 * Combo window for a 1-based combo stage, mirroring the COMBO_STAGE_*_WINDOW
	 * constants. Exposed so the fidelity tests can compare the shipped values
	 * against AnimationFrameData.md without duplicating the numbers.
	 */
	UFUNCTION(BlueprintCallable, BlueprintPure, Category = "Combat")
	float GetComboWindowSeconds(int32 Stage) const;

	//=============================================================================
	// GUARD SYSTEM
	//=============================================================================

	UFUNCTION(BlueprintCallable, Category = "Combat")
	void StartGuard();

	UFUNCTION(BlueprintCallable, Category = "Combat")
	void EndGuard();

	UFUNCTION(BlueprintCallable, BlueprintPure, Category = "Combat")
	bool IsGuarding() const { return bIsGuarding; }

	UFUNCTION(BlueprintCallable, BlueprintPure, Category = "Combat")
	bool IsPerfectGuard() const { return bPerfectGuard; }

	//=============================================================================
	// PERFECT GUARD SYSTEM
	//=============================================================================

	// Called by enemy attack system when attack connects.
	// If player released guard within PerfectGuardWindow before this moment, triggers perfect guard.
	UFUNCTION(BlueprintCallable, Category = "Combat")
	void CheckPerfectGuard();

	//=============================================================================
	// QUICK STEP SYSTEM
	//=============================================================================

	UFUNCTION(BlueprintCallable, Category = "Combat")
	void QuickStep(FVector Direction);

	UFUNCTION(BlueprintCallable, BlueprintPure, Category = "Combat")
	bool IsInvulnerable() const { return bIsInvulnerable; }

	UFUNCTION(BlueprintCallable, BlueprintPure, Category = "Combat")
	bool CanDoubleStep() const { return bCanDoubleStep; }

	//=============================================================================
	// DAMAGE
	//=============================================================================

	UFUNCTION(BlueprintCallable, Category = "Combat")
	void TakeDamage(float DamageAmount, EDamageType DamageType);

	UFUNCTION(BlueprintCallable, BlueprintPure, Category = "Combat")
	float GetHealth() const { return CurrentHealth; }

	UFUNCTION(BlueprintCallable, BlueprintPure, Category = "Combat")
	float GetMaxHealth() const { return MaxHealth; }

	UFUNCTION(BlueprintCallable, Category = "Combat")
	void SetHealth(float NewHealth);

	UFUNCTION(BlueprintCallable, Category = "Combat")
	void SetMaxHealth(float NewMaxHealth);

	UFUNCTION(BlueprintCallable, BlueprintPure, Category = "Combat")
	float GetMana() const { return Mana; }

	UFUNCTION(BlueprintCallable, BlueprintPure, Category = "Combat")
	float GetMaxMana() const { return MaxMana; }

	UFUNCTION(BlueprintCallable, Category = "Combat")
	void SetMana(float NewMana);

	UFUNCTION(BlueprintCallable, Category = "Combat")
	void SetMaxMana(float NewMaxMana);

	UFUNCTION(BlueprintCallable, BlueprintPure, Category = "Combat")
	TArray<FString> GetEquippedWeapons() const { return EquippedWeapons; }

	UFUNCTION(BlueprintCallable, Category = "Combat")
	void SetEquippedWeapons(const TArray<FString>& NewWeapons) { EquippedWeapons = NewWeapons; }

	UFUNCTION(BlueprintCallable, Category = "Combat")
	void ApplyDeathDoll();

	UFUNCTION(BlueprintCallable, BlueprintPure, Category = "Combat")
	bool HasDeathDoll() const { return bHasDeathDoll; }

	UFUNCTION(BlueprintCallable, Category = "Combat")
	void SetDeathDoll(bool bHas);

	//=============================================================================
	// WEAPON
	//=============================================================================

	UFUNCTION(BlueprintCallable, Category = "Combat")
	void EquipWeapon(EWeaponType NewWeaponType);

	/** Equip an exact forged weapon by its data-table row name. */
	UFUNCTION(BlueprintCallable, Category = "Combat")
	bool EquipWeaponByName(FName WeaponName);

	UFUNCTION(BlueprintCallable, BlueprintPure, Category = "Combat")
	EWeaponType GetCurrentWeaponType() const { return CurrentWeaponType; }

	UFUNCTION(BlueprintCallable, BlueprintPure, Category = "Combat")
	FWeaponData GetCurrentWeaponData() const { return CurrentWeaponData; }

	UFUNCTION(BlueprintCallable, BlueprintPure, Category = "Combat")
	FWeaponData GetWeaponDataByName(FName WeaponName) const;

	UFUNCTION(BlueprintCallable, BlueprintPure, Category = "Combat")
	TArray<FName> GetKnownWeaponNames() const;

protected:
	// Weapon rows imported from DT_WeaponDataTable. Assigned on the Hector
	// Blueprint so combat stats stay data-driven.
	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Combat|Data")
	TObjectPtr<UDataTable> WeaponDataTableAsset;

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Combat|Data")
	FName DefaultWeaponName = "Short Sword";

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Combat|Trace")
	float AttackTraceRadius = 90.0f;

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Combat|Trace")
	float AttackTraceForwardOffset = 80.0f;

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Combat|Trace")
	float AttackHitDelay = 0.12f;

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Combat")
	float MaxHealth = 100.0f;

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Combat")
	float PerfectGuardWindow = PERFECT_GUARD_WINDOW;

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Combat")
	float QuickStepIframes = QUICK_STEP_IFRAMES;

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Combat")
	float DoubleStepWindow = DOUBLE_STEP_WINDOW;

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Combat")
	TMap<EWeaponType, FWeaponData> WeaponDataTable;

private:
	// Combo state
	int32 CurrentComboStage = 0;
	float ComboTimer = 0.0f;
	bool bIsAttacking = false;
	bool bComboWindowOpen = false;

	// Guard state
	bool bIsGuarding = false;
	bool bPerfectGuard = false;
	float GuardStartTime = 0.0f;
	float LastGuardReleaseTime = 0.0f;
	bool bWasRecentlyGuarding = false;

	// Mana
	float Mana = 100.0f;
	float MaxMana = 100.0f;

	// Equipped weapons (saved as weapon names)
	TArray<FString> EquippedWeapons;

	// Quick step state
	bool bIsInvulnerable = false;
	float InvulnerabilityTimer = 0.0f;
	bool bCanDoubleStep = false;
	float DoubleStepTimer = 0.0f;
	float LastQuickStepTime = 0.0f;

	// Health
	float CurrentHealth = 100.0f;

	// Death Doll - Hector dies instead of player (one-time use)
	bool bHasDeathDoll = false;

	// Weapon
	EWeaponType CurrentWeaponType = EWeaponType::Sword;
	FWeaponData CurrentWeaponData;
	TMap<FName, FWeaponData> WeaponDataByName;

	// Timers
	FTimerHandle ComboResetTimer;
	FTimerHandle InvulnerabilityTimerHandle;
	FTimerHandle DoubleStepTimerHandle;
	FTimerHandle AttackStateTimer;
	FTimerHandle AttackHitTimer;

	void LoadWeaponData();
	void UpdateCombo(float DeltaTime);
	void UpdateInvulnerability(float DeltaTime);
	void UpdateDoubleStep(float DeltaTime);
	void ApplyDamageReduction(float& Damage, EDamageType DamageType);
	void PlayAttackMontage(int32 Stage);
	void PlayFinalAttackMontage(int32 Stage);

	/** Sweep the weapon arc and damage every enemy hit once. */
	void ApplyAttackHit(int32 ComboStage, bool bHeavyAttack);
	void EndAttack();
	float GetAttackDuration() const;
};