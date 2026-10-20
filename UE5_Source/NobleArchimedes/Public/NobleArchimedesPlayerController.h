// Fill out your copyright notice in the Description page of Project Settings.

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/PlayerController.h"
#include "NobleArchimedesPlayerController.generated.h"

class AHectorCharacter;

UCLASS()
class NOBLEARCHIMEDES_API ANobleArchimedesPlayerController : public APlayerController
{
	GENERATED_BODY()

public:
	ANobleArchimedesPlayerController();

	virtual void BeginPlay() override;
	virtual void SetupInputComponent() override;

	//=============================================================================
	// INPUT HANDLING
	//=============================================================================

	UFUNCTION(BlueprintCallable, Category = "Player")
	void PauseGame();

	UFUNCTION(BlueprintCallable, Category = "Player")
	void OpenMap();

	UFUNCTION(BlueprintCallable, Category = "Player")
	void ToggleCameraMode();

	UFUNCTION(BlueprintCallable, Category = "Player")
	void UseStealFocus();

	UFUNCTION(BlueprintCallable, Category = "Player")
	void ToggleLockOn();

	//=============================================================================
	// PLAYER REFERENCE
	//=============================================================================

	UFUNCTION(BlueprintCallable, BlueprintPure, Category = "Player")
	AHectorCharacter* GetHectorCharacter() const;

private:
	mutable AHectorCharacter* CachedHectorCharacter;

	void CacheHectorCharacter();
};