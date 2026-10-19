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

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
	UNobleArchimedesItemSystem* ItemSystem;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
	USpringArmComponent* CameraBoom;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
	UCameraComponent* FollowCamera;

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
	void SetHealth(float NewHealth) { if (CombatComponent) CombatComponent->SetHealth(NewHealth); }

	UFUNCTION(BlueprintCallable, Category = "Combat")
	void SetMaxHealth(float NewMaxHealth) { if (CombatComponent) CombatComponent->SetMaxHealth(NewMaxHealth); }

	UFUNCTION(BlueprintCallable, BlueprintPure, Category = "Combat")
	float GetMana() const { return CombatComponent ? CombatComponent->GetMana() : 100.0f; }

	UFUNCTION(BlueprintCallable, BlueprintPure, Category = "Combat")
	float GetMaxMana() const { return CombatComponent ? CombatComponent->GetMaxMana() : 100.0f; }

	UFUNCTION(BlueprintCallable, Category = "Combat")
	void SetMana(float NewMana) { if (CombatComponent) CombatComponent->SetMana(NewMana); }

	UFUNCTION(BlueprintCallable, Category = "Combat")
	void SetMaxMana(float NewMaxMana) { if (CombatComponent) CombatComponent->SetMaxMana(NewMaxMana); }

	UFUNCTION(BlueprintCallable, BlueprintPure, Category = "Combat")
	int32 GetLevel() const { return Level; }

	UFUNCTION(BlueprintCallable, Category = "Combat")
	void SetLevel(int32 NewLevel) { Level = NewLevel; }

	UFUNCTION(BlueprintCallable, BlueprintPure, Category = "Combat")
	int32 GetExperience() const { return Experience; }

	UFUNCTION(BlueprintCallable, Category = "Combat")
	void SetExperience(int32 NewExperience) { Experience = NewExperience; }

	UFUNCTION(BlueprintCallable, BlueprintPure, Category = "Combat")
	int32 GetSkillPoints() const { return SkillPoints; }

	UFUNCTION(BlueprintCallable, Category = "Combat")
	void SetSkillPoints(int32 NewSkillPoints) { SkillPoints = NewSkillPoints; }

	UFUNCTION(BlueprintCallable, BlueprintPure, Category = "Combat")
	FString GetPlayerName() const { return PlayerName; }

	UFUNCTION(BlueprintCallable, Category = "Combat")
	void SetPlayerName(const FString& NewName) { PlayerName = NewName; }

	UFUNCTION(BlueprintCallable, BlueprintPure, Category = "Combat")
	TArray<FInventoryItem> GetInventoryItems() const { return InventoryItems; }

	UFUNCTION(BlueprintCallable, Category = "Combat")
	void SetInventoryItems(const TArray<FInventoryItem>& NewItems) { InventoryItems = NewItems; }

	UFUNCTION(BlueprintCallable, BlueprintPure, Category = "Combat")
	TArray<FString> GetEquippedWeapons() const { return CombatComponent ? CombatComponent->GetEquippedWeapons() : TArray<FString>(); }

	UFUNCTION(BlueprintCallable, BlueprintPure, Category = "Combat")
	EWeaponType GetEquippedWeaponType() const { return CombatComponent ? CombatComponent->GetCurrentWeaponType() : EWeaponType::Sword; }

	UFUNCTION(BlueprintCallable, Category = "Combat")
	void SetEquippedWeaponType(EWeaponType NewWeaponType) { if (CombatComponent) CombatComponent->EquipWeapon(NewWeaponType); }

	UFUNCTION(BlueprintCallable, BlueprintPure, Category = "Combat")
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

	UFUNCTION(BlueprintCallable, BlueprintPure, Category = "Items")
	UNobleArchimedesItemSystem* GetItemSystem() const;

	// Active innocent devil index (index into InnocentDevils array)
	UFUNCTION(BlueprintCallable, BlueprintPure, Category = "Innocent Devil")
	int32 GetActiveInnocentDevilIndex() const;

	UFUNCTION(BlueprintCallable, Category = "Innocent Devil")
	void SetActiveInnocentDevilIndex(int32 NewIndex);

	UFUNCTION(BlueprintCallable, Category = "Innocent Devil")
	void SetUnlockedInnocentDevils(TArray<EInnocentDevilType> NewUnlocked);

	UFUNCTION(BlueprintCallable, Category = "SaveLoad")
	void SetDiscoveredRecipes(TArray<FName> NewRecipes);

	UFUNCTION(BlueprintCallable, Category = "SaveLoad")
	void SetForgedWeapons(TArray<FName> NewWeapons);

	// Types of innocent devils that have been unlocked
	UFUNCTION(BlueprintCallable, BlueprintPure, Category = "Innocent Devil")
	TArray<EInnocentDevilType> GetUnlockedInnocentDevils() const;

	// Discovered weapon forge recipes (saved as recipe names)
	UFUNCTION(BlueprintCallable, BlueprintPure, Category = "SaveLoad")
	TArray<FName> GetDiscoveredRecipes() const;

	// Forged weapons (saved as weapon names)
	UFUNCTION(BlueprintCallable, BlueprintPure, Category = "SaveLoad")
	TArray<FName> GetForgedWeapons() const;

	// Audio volume settings
	UFUNCTION(BlueprintCallable, BlueprintPure, Category = "SaveLoad")
	float GetMasterVolume() const;

	UFUNCTION(BlueprintCallable, BlueprintPure, Category = "SaveLoad")
	float GetSFXVolume() const;

	UFUNCTION(BlueprintCallable, BlueprintPure, Category = "SaveLoad")
	float GetMusicVolume() const;

private:
	FVector MoveInputVector;
	FVector LookInputVector;

	// Save/load player data
	FString PlayerName = "Hector";
	int32 Level = 1;
	int32 Experience = 0;
	int32 SkillPoints = 0;
	TArray<FInventoryItem> InventoryItems;
};