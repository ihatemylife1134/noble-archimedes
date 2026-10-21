// Fill out your copyright notice in the Description page of Project Settings.

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "NobleArchimedesTypes.h"
#include "EnemyBase.generated.h"

DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnDefeated, AEnemyBase*, DefeatedEnemy);

class AItemDrop;

UCLASS()
class NOBLEARCHIMEDES_API AEnemyBase : public ACharacter
{
	GENERATED_BODY()

public:
	// Sets default values for this actor's properties
	AEnemyBase();

protected:
	// Called when the game starts or when spawned
	virtual void BeginPlay() override;

public:
	// Called every frame
	virtual void Tick(float DeltaTime) override;

	//=============================================================================
	// ENEMY PROPERTIES
	//=============================================================================

	UPROPERTY(EditDefaultsOnly, BlueprintReadWrite, Category = "Enemy")
	FName EnemyName;

	UPROPERTY(EditDefaultsOnly, BlueprintReadWrite, Category = "Enemy")
	int32 ChapterNumber;

	UPROPERTY(EditDefaultsOnly, BlueprintReadWrite, Category = "Enemy")
	float Health = 50.0f;

	UPROPERTY(EditDefaultsOnly, BlueprintReadWrite, Category = "Enemy")
	float MaxHealth = 50.0f;

	UPROPERTY(EditDefaultsOnly, BlueprintReadWrite, Category = "Enemy")
	float Damage = 10.0f;

	UPROPERTY(EditDefaultsOnly, BlueprintReadWrite, Category = "Enemy")
	float AttackRange = 150.0f;

	UPROPERTY(EditDefaultsOnly, BlueprintReadWrite, Category = "Enemy")
	float DetectionRange = 600.0f;

	UPROPERTY(EditDefaultsOnly, BlueprintReadWrite, Category = "Enemy")
	FString Weaknesses; // Comma-separated damage type names

	UPROPERTY(EditDefaultsOnly, BlueprintReadWrite, Category = "Enemy")
	FString Tolerances; // Comma-separated damage type names

	UPROPERTY(EditDefaultsOnly, BlueprintReadWrite, Category = "Enemy")
	FString ItemDrops; // Comma-separated item names

	UPROPERTY(EditDefaultsOnly, BlueprintReadWrite, Category = "Enemy")
	bool CanBeStolen = false;

	UPROPERTY(EditDefaultsOnly, BlueprintReadWrite, Category = "Enemy")
	FName StealItem;

	UPROPERTY(EditDefaultsOnly, BlueprintReadWrite, Category = "Enemy")
	float StealChance = 0.3f;

	UPROPERTY(EditDefaultsOnly, BlueprintReadWrite, Category = "Enemy")
	float StealWindowSeconds = 10.0f;

	UPROPERTY(EditDefaultsOnly, BlueprintReadWrite, Category = "Enemy")
	float PatrolSpeed = 300.0f;

	UPROPERTY(EditDefaultsOnly, BlueprintReadWrite, Category = "Enemy")
	float ChaseSpeed = 350.0f;

	UPROPERTY(EditDefaultsOnly, BlueprintReadWrite, Category = "Enemy")
	float AttackCooldown = 2.0f;

	/** Delay between the attack animation starting and the hit landing. */
	UPROPERTY(EditDefaultsOnly, BlueprintReadWrite, Category = "Enemy")
	float AttackWindup = 0.35f;

	UPROPERTY(EditDefaultsOnly, BlueprintReadWrite, Category = "Enemy")
	EDamageType AttackDamageType = EDamageType::Slash;

	UPROPERTY(EditDefaultsOnly, BlueprintReadWrite, Category = "Enemy")
	TSubclassOf<AItemDrop> ItemDropClass;

	UPROPERTY(EditDefaultsOnly, BlueprintReadWrite, Category = "Enemy")
	bool bIsBoss = false;

	UPROPERTY(EditDefaultsOnly, BlueprintReadWrite, Category = "Enemy")
	int32 BossPhase = 1;

	//=============================================================================
	// ENEMY STATE
	//=============================================================================

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Enemy")
	float CurrentHealth;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Enemy")
	float LastAttackTime = 0.0f;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Enemy")
	bool bCanSeePlayer = false;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Enemy")
	bool bIsInAttackRange = false;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Enemy")
	bool bIsStealable = false;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Enemy")
	float StealWindowTimer = 0.0f;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Enemy")
	bool bHasBeenStolenFrom = false;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Enemy")
	bool bIsDead = false;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Enemy")
	bool bIsAttacking = false;

	//=============================================================================
	// DELEGATES
	//=============================================================================

	UPROPERTY(BlueprintAssignable, Category = "Enemy")
	FOnDefeated OnDefeated;

	//=============================================================================
	// ENEMY ACTIONS
	//=============================================================================

	UFUNCTION(BlueprintCallable, Category = "Enemy")
	void ApplyDamage(float DamageAmount, EDamageType DamageType);

	UFUNCTION(BlueprintCallable, Category = "Enemy")
	void FacePlayer();

	UFUNCTION(BlueprintCallable, Category = "Enemy")
	void MoveToPlayer();

	UFUNCTION(BlueprintCallable, Category = "Enemy")
	void MoveToPatrolPoint();

	UFUNCTION(BlueprintCallable, Category = "Enemy")
	void PlayAttackAnimation();

	UFUNCTION(BlueprintCallable, Category = "Enemy")
	void PlayChaseAnimation();

	UFUNCTION(BlueprintCallable, Category = "Enemy")
	void PlayIdleAnimation();

	UFUNCTION(BlueprintCallable, BlueprintPure, Category = "Enemy")
	bool CanBeStolenByPlayer() const;

	UFUNCTION(BlueprintCallable, Category = "Enemy")
	void StartStealWindow();

	UFUNCTION(BlueprintCallable, Category = "Enemy")
	void EndStealWindow();

	UFUNCTION(BlueprintCallable, Category = "Enemy")
	bool TrySteal(FName& OutStolenItem);

	UFUNCTION(BlueprintCallable, Category = "Enemy")
	void ApplyDamageToPlayer(class AHectorCharacter* Player);

protected:
	UFUNCTION()
	void OnPlayerDetected(class AActor* DetectedActor);

	UFUNCTION()
	void OnPlayerLost(class AActor* LostActor);

private:
	float LastPerceptionUpdate = 0.0f;
	float PatrolWaitTimer = 0.0f;
	int32 CurrentPatrolIndex = 0;

	FTimerHandle AttackTimer;
	FTimerHandle DeathTimer;

	void UpdatePerception(float DeltaTime);
	void CheckAttackRange();
	void UpdateStealWindow(float DeltaTime);
	void PerformAttack();
	void DropLoot();
	void Die();
	void DestroySelf();
};
