// Fill out your copyright notice in the Description page of Project Settings.

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "NobleArchimedesTypes.h"
#include "InnocentDevilActor.generated.h"

UCLASS()
class NOBLEARCHIMEDES_API AInnocentDevilActor : public ACharacter
{
	GENERATED_BODY()

public:
	// Sets default values for this actor's properties
	AInnocentDevilActor();

protected:
	// Called when the game starts or when spawned
	virtual void BeginPlay() override;

public:
	// Called every frame
	virtual void Tick(float DeltaTime) override;

	//=============================================================================
	// INNOCENT DEVIL PROPERTIES
	//=============================================================================

	UPROPERTY(EditDefaultsOnly, BlueprintReadWrite, Category = "Innocent Devil")
	FInnocentDevilData DevilData;

	UPROPERTY(EditDefaultsOnly, BlueprintReadWrite, Category = "Innocent Devil")
	EInnocentDevilMode DevilMode = EInnocentDevilMode::Auto;

	UPROPERTY(EditDefaultsOnly, BlueprintReadWrite, Category = "Innocent Devil")
	bool bIsSummoned = false;

	UPROPERTY(EditDefaultsOnly, BlueprintReadWrite, Category = "Innocent Devil")
	class AHectorCharacter* OwnerHector = nullptr;

	UPROPERTY(EditDefaultsOnly, BlueprintReadWrite, Category = "Innocent Devil")
	float AttackCooldown = 1.5f;

	UPROPERTY(EditDefaultsOnly, BlueprintReadWrite, Category = "Innocent Devil")
	float AttackRange = 600.0f;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Innocent Devil")
	float LastDevilAttackTime = 0.0f;

	//=============================================================================
	// INNOCENT DEVIL ACTIONS
	//=============================================================================

	UFUNCTION(BlueprintCallable, Category = "Innocent Devil")
	void InitializeDevil(const FInnocentDevilData& NewDevilData, class AHectorCharacter* NewOwner);

	UFUNCTION(BlueprintCallable, Category = "Innocent Devil")
	void SetDevilMode(EInnocentDevilMode NewMode);

	UFUNCTION(BlueprintCallable, Category = "Innocent Devil")
	void CommandAttack();

	UFUNCTION(BlueprintCallable, Category = "Innocent Devil")
	void CommandGuard();

	UFUNCTION(BlueprintCallable, Category = "Innocent Devil")
	void CommandHeal();

	UFUNCTION(BlueprintCallable, Category = "Innocent Devil")
	void EvolveDevil();

	UFUNCTION(BlueprintCallable, BlueprintPure, Category = "Innocent Devil")
	bool IsSummoned() const { return bIsSummoned; }

	UFUNCTION(BlueprintCallable, BlueprintPure, Category = "Innocent Devil")
	EInnocentDevilMode GetDevilMode() const { return DevilMode; }

protected:
	void UpdateDevilAI(float DeltaTime);
	void FollowOwner();
	void AttackTarget();
	void GuardOwner();
	void HealOwner();

private:
	float DevilAIUpdateTimer = 0.0f;
	float DevilAIUpdateInterval = 0.5f; // Update AI every 0.5s
};
