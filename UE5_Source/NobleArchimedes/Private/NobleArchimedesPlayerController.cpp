// Fill out your copyright notice in the Description page of Project Settings.

#include "NobleArchimedesPlayerController.h"
#include "HectorCharacter.h"
#include "Kismet/GameplayStatics.h"
#include "GameFramework/GameModeBase.h"
#include "EnhancedInputComponent.h"

ANobleArchimedesPlayerController::ANobleArchimedesPlayerController()
{
	bShowMouseCursor = false;
	bEnableClickEvents = false;
	bEnableTouchEvents = false;
}

void ANobleArchimedesPlayerController::BeginPlay()
{
	Super::BeginPlay();
	CacheHectorCharacter();
}

void ANobleArchimedesPlayerController::SetupInputComponent()
{
	Super::SetupInputComponent();
}

void ANobleArchimedesPlayerController::PauseGame()
{
	if (GetWorld())
	{
		UGameplayStatics::SetGamePaused(GetWorld(), true);
	}
}

void ANobleArchimedesPlayerController::OpenMap()
{
	// Open map UI widget
}

void ANobleArchimedesPlayerController::ToggleCameraMode()
{
	if (AHectorCharacter* Hector = GetHectorCharacter())
	{
		// Camera mode toggle is handled in HectorCharacter
	}
}

void ANobleArchimedesPlayerController::UseStealFocus()
{
	// Activate steal focus mode on targeted enemy
}

void ANobleArchimedesPlayerController::ToggleLockOn()
{
	// Toggle lock-on to nearest enemy
}

AHectorCharacter* ANobleArchimedesPlayerController::GetHectorCharacter() const
{
	if (!CachedHectorCharacter)
	{
		CachedHectorCharacter = Cast<AHectorCharacter>(GetPawn());
	}
	return CachedHectorCharacter;
}

void ANobleArchimedesPlayerController::CacheHectorCharacter()
{
	CachedHectorCharacter = Cast<AHectorCharacter>(GetPawn());
}