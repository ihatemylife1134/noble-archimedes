// Fill out your copyright notice in the Description page of Project Settings.

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "NobleArchimedesTypes.h"
#include "NobleArchimedesCombatComponent.h"
#include "NobleArchimedesCharacter.generated.h"

class UNobleArchimedesCameraComponent;
class UNobleArchimedesCompanionComponent;

UCLASS()
class NOBLEARCHIMEDES_API ANobleArchimedesCharacter : public ACharacter
{
	GENERATED_BODY()

public:
	ANobleArchimedesCharacter();

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
	UNobleArchimedesCompanionComponent* CompanionComponent;

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

	//=============================================================================
	// CAMERA MODE
	//=============================================================================

	UFUNCTION(BlueprintCallable, Category = "Camera")
	void SetCameraMode(ECameraMode NewMode);

	UFUNCTION(BlueprintCallable, BlueprintPure, Category = "Camera")
	ECameraMode GetCameraMode() const;

	//=============================================================================
	// COMPANION
	//=============================================================================

	UFUNCTION(BlueprintCallable, Category = "Companion")
	void SummonCompanion(ECompanionType Type);

	UFUNCTION(BlueprintCallable, Category = "Companion")
	void SetCompanionMode(ECompanionMode Mode);

	UFUNCTION(BlueprintCallable, BlueprintPure, Category = "Companion")
	TArray<FCompanionData> GetCompanions() const;

private:
	FVector MoveInputVector;
	FVector LookInputVector;
};