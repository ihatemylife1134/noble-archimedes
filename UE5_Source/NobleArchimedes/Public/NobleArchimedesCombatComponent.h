// Fill out your copyright notice in the Description page of Project Settings.

#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "NobleArchimedesTypes.h"
#include "NobleArchimedesCombatComponent.generated.h"

class ANobleArchimedesCharacter;

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

	//=============================================================================
	// WEAPON
	//=============================================================================

	UFUNCTION(BlueprintCallable, Category = "Combat")
	void EquipWeapon(EWeaponType NewWeaponType);

	UFUNCTION(BlueprintCallable, BlueprintPure, Category = "Combat")
	EWeaponType GetCurrentWeaponType() const { return CurrentWeaponType; }

	UFUNCTION(BlueprintCallable, BlueprintPure, Category = "Combat")
	FWeaponData GetCurrentWeaponData() const { return CurrentWeaponData; }

protected:
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

	// Quick step state
	bool bIsInvulnerable = false;
	float InvulnerabilityTimer = 0.0f;
	bool bCanDoubleStep = false;
	float DoubleStepTimer = 0.0f;
	float LastQuickStepTime = 0.0f;

	// Health
	float CurrentHealth = 100.0f;

	// Weapon
	EWeaponType CurrentWeaponType = EWeaponType::Sword;
	FWeaponData CurrentWeaponData;

	// Timers
	FTimerHandle ComboResetTimer;
	FTimerHandle InvulnerabilityTimerHandle;
	FTimerHandle DoubleStepTimerHandle;

	void UpdateCombo(float DeltaTime);
	void UpdateInvulnerability(float DeltaTime);
	void UpdateDoubleStep(float DeltaTime);
	void CheckPerfectGuard();
	void ApplyDamageReduction(float& Damage, EDamageType DamageType);
	void PlayAttackMontage(int32 Stage);
	void PlayFinalAttackMontage(int32 Stage);
};