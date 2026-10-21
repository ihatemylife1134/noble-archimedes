// Fill out your copyright notice in the Description page of Project Settings.

#pragma once

#include "CoreMinimal.h"
#include "Room.h"
#include "SaveRoom.generated.h"

UCLASS()
class NOBLEARCHIMEDES_API ASaveRoom : public ARoom
{
	GENERATED_BODY()

public:
	// Sets default values for this actor's properties
	ASaveRoom();

protected:
	// Called when the game starts or when spawned
	virtual void BeginPlay() override;

public:
	//=============================================================================
	// SAVE ROOM MECHANICS
	//=============================================================================

	UPROPERTY(EditDefaultsOnly, BlueprintReadWrite, Category = "SaveRoom")
	bool bAutoSaveOnEntry = true;

	UPROPERTY(EditDefaultsOnly, BlueprintReadWrite, Category = "SaveRoom")
	FName SaveSlotName = "AutoSave";

	UFUNCTION(BlueprintCallable, Category = "SaveRoom")
	void ActivateSaveRoom(class AHectorCharacter* Player);

	UFUNCTION(BlueprintCallable, Category = "SaveRoom")
	void FullHealPlayer(class AHectorCharacter* Player);

private:
	UFUNCTION()
	void OnPlayerEnterSaveRoom(UPrimitiveComponent* OverlappedComponent, AActor* OtherActor,
		UPrimitiveComponent* OtherComp, int32 OtherBodyIndex, bool bFromSweep, const FHitResult& SweepResult);
};
