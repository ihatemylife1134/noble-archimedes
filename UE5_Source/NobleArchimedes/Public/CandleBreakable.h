// Fill out your copyright notice in the Description page of Project Settings.

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "Components/StaticMeshComponent.h"
#include "Particles/ParticleSystemComponent.h"
#include "NobleArchimedesTypes.h"
#include "CandleBreakable.generated.h"

class AItemDrop;

UCLASS()
class NOBLEARCHIMEDES_API ACandleBreakable : public AActor
{
	GENERATED_BODY()

public:
	// Sets default values for this actor's properties
	ACandleBreakable();

protected:
	// Called when the game starts or when spawned
	virtual void BeginPlay() override;

public:
	// Called every frame
	virtual void Tick(float DeltaTime) override;

	//=============================================================================
	// CANDLE PROPERTIES
	//=============================================================================

	UPROPERTY(EditDefaultsOnly, BlueprintReadWrite, Category = "Candle")
	bool bIsBroken = false;

	UPROPERTY(EditDefaultsOnly, BlueprintReadWrite, Category = "Candle")
	TArray<FName> PossibleDrops; // Item names that can drop

	UPROPERTY(EditDefaultsOnly, BlueprintReadWrite, Category = "Candle")
	float DropChance = 0.3f; // 30% base chance to drop an item

	UPROPERTY(EditDefaultsOnly, BlueprintReadWrite, Category = "Candle")
	TSubclassOf<AItemDrop> ItemDropClass;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Candle")
	UStaticMeshComponent* CandleMesh;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Candle")
	UParticleSystemComponent* FlameParticle;

	//=============================================================================
	// CANDLE INTERACTION
	//=============================================================================

	UFUNCTION(BlueprintCallable, Category = "Candle")
	void BreakCandle();

	UFUNCTION(BlueprintCallable, BlueprintPure, Category = "Candle")
	bool IsCandleBroken() const;

private:
	TArray<FName> ItemDropTable; // Populated from data table on begin play

	UFUNCTION()
	void OnCandleHit(UPrimitiveComponent* HitComponent, AActor* OtherActor, UPrimitiveComponent* OtherComp,
		FVector NormalImpulse, const FHitResult& Hit);

	void SpawnDropItem(FName ItemName);
};
