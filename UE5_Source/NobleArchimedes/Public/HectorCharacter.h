// Fill out your copyright notice in the Description page of Project Settings.

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "NobleArchimedesTypes.h"
#include "NobleArchimedesCombatComponent.h"
#include "HectorCharacter.generated.h"

class UNobleArchimedesCameraComponent;
class UNobleArchimedesInnocentDevilComponent;

UCLASS()
class NOBLEARCHIMEDES_API AHectorCharacter : public ACharacter
{
	GENERATED_BODY()

public:
	AHectorCharacter();

protected:
	virtual void BeginPlay() override;

public:
	virtual void Tick(float DeltaTime) override;
	virtual void SetupPlayerInputComponent(class UInputComponent* PlayerInputComponent) override;

	//=============================================================================
	// COMPONENTS
	//=============================================================================

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
	UNobleArchimedesCombatComponent* CombatComponent;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
	UNobleArchimedesCameraComponent* CameraComponent;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
	UNobleArchimedesInnocentDevilComponent* InnocentDevilComponent;

	//=============================================================================
	// MOVEMENT
	//=============================================================================

	UFUNCTION(BlueprintCallable, Category = "Movement")
	void Move(float ValueX, float ValueY);

	UFUNCTION(BlueprintCallable, Category = "Movement")
	void Look(float ValueX, float ValueY);

	//=============================================================================
	// COMBAT (delegated to CombatComponent)
	//=============================================================================

	UFUNCTION(BlueprintCallable, Category = "Combat")
	void LightAttack() { if (CombatComponent) CombatComponent->LightAttack(); }

	UFUNCTION(BlueprintCallable, Category = "Combat")
	void HeavyAttack() { if (CombatComponent) CombatComponent->HeavyAttack(); }

	UFUNCTION(BlueprintCallable, Category = "Combat")
	void StartGuard() { if (CombatComponent) CombatComponent->StartGuard(); }

	UFUNCTION(BlueprintCallable, Category = "Combat")
	void EndGuard() { if (CombatComponent) CombatComponent->EndGuard(); }

	UFUNCTION(BlueprintCallable, Category = "Combat")
	void QuickStep(FVector Direction) { if (CombatComponent) CombatComponent->QuickStep(Direction); }

	UFUNCTION(BlueprintCallable, Category = "Combat")
	void StealTargetFocus() { /* Lock-on target for stealing */ }

	UFUNCTION(BlueprintCallable, Category = "Combat")
	void TakeDamage(float Damage, EDamageType DamageType) { if (CombatComponent) CombatComponent->TakeDamage(Damage, DamageType); }

	UFUNCTION(BlueprintCallable, Category = "Combat")
	void EquipWeapon(EWeaponType WeaponType) { if (CombatComponent) CombatComponent->EquipWeapon(WeaponType); }

	UFUNCTION(BlueprintCallable, BlueprintPure, Category = "Combat")
	bool IsInvulnerable() const { return CombatComponent ? CombatComponent->IsInvulnerable() : false; }

	UFUNCTION(BlueprintCallable, BlueprintPure, Category = "Combat")
	bool IsPerfectGuard() const { return CombatComponent ? CombatComponent->IsPerfectGuard() : false; }

	UFUNCTION(BlueprintCallable, BlueprintPure, Category = "Combat")
	float GetHealth() const { return CombatComponent ? CombatComponent->GetHealth() : 0.0f; }

	UFUNCTION(BlueprintCallable, BlueprintPure, Category = "Combat")
	float GetMaxHealth() const { return CombatComponent ? CombatComponent->GetMaxHealth() : 100.0f; }

	UFUNCTION(BlueprintCallable, Category = "Combat")
	bool HasDeathDoll() const { return CombatComponent ? CombatComponent->HasDeathDoll() : false; }

	UFUNCTION(BlueprintCallable, Category = "Combat")
	void SetDeathDoll(bool bHas) { if (CombatComponent) CombatComponent->SetDeathDoll(bHas); }

	//=============================================================================
	// CAMERA MODE
	//=============================================================================

	UFUNCTION(BlueprintCallable, Category = "Camera")
	void SetCameraMode(ECameraMode NewMode);

	UFUNCTION(BlueprintCallable, BlueprintPure, Category = "Camera")
	ECameraMode GetCameraMode() const;

	//=============================================================================
	// INNOCENT DEVIL
	//=============================================================================

	UFUNCTION(BlueprintCallable, Category = "Innocent Devil")
	void SummonInnocentDevil(EInnocentDevilType Type);

	UFUNCTION(BlueprintCallable, Category = "Innocent Devil")
	void SetInnocentDevilMode(EInnocentDevilMode Mode);

	UFUNCTION(BlueprintCallable, BlueprintPure, Category = "Innocent Devil")
	TArray<FInnocentDevilData> GetInnocentDevils() const;

private:
	FVector MoveInputVector;
	FVector LookInputVector;
};