// Fill out your copyright notice in the Description page of Project Settings.

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "Components/StaticMeshComponent.h"
#include "Components/BoxComponent.h"
#include "TimerManager.h"
#include "ItemDrop.generated.h"

UCLASS()
class NOBLEARCHIMEDES_API AItemDrop : public AActor
{
	GENERATED_BODY()

public:
	// Sets default values for this actor's properties
	AItemDrop();

protected:
	// Called when the game starts or when spawned
	virtual void BeginPlay() override;

public:
	// Called every frame
	virtual void Tick(float DeltaTime) override;

	//=============================================================================
	// ITEM PROPERTIES
	//=============================================================================

	UPROPERTY(EditDefaultsOnly, BlueprintReadWrite, Category = "Item")
	FName ItemName;

	UPROPERTY(EditDefaultsOnly, BlueprintReadWrite, Category = "Item")
	bool bIsStealOnly = false;

	UPROPERTY(EditDefaultsOnly, BlueprintReadWrite, Category = "Item")
	bool bIsRare = false;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Item")
	UStaticMeshComponent* ItemMesh;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Item")
	UBoxComponent* PickupTrigger;

	UPROPERTY(EditDefaultsOnly, BlueprintReadWrite, Category = "Item")
	float AutoDestroyTime = 30.0f; // Seconds before item disappears

	//=============================================================================
	// ITEM ACTIONS
	//=============================================================================

	UFUNCTION(BlueprintCallable, Category = "Item")
	void InitializeItem(FName NewItemName, bool NewIsStealOnly, bool NewIsRare);

	UFUNCTION(BlueprintCallable, Category = "Item")
	void PickupItem(class AHectorCharacter* Player);

	UFUNCTION(BlueprintCallable, BlueprintPure, Category = "Item")
	bool IsStealOnly() const { return bIsStealOnly; }

	UFUNCTION(BlueprintCallable, BlueprintPure, Category = "Item")
	bool IsRare() const { return bIsRare; }

private:
	UPROPERTY()
	FTimerHandle AutoDestroyTimerHandle;

	UFUNCTION()
	void OnPlayerEnterPickup(UPrimitiveComponent* OverlappedComponent, AActor* OtherActor,
		UPrimitiveComponent* OtherComp, int32 OtherBodyIndex, bool bFromSweep, const FHitResult& SweepResult);

	UFUNCTION()
	void AutoDestroy();
};
