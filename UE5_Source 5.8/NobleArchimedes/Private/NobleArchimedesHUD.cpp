// Fill out your copyright notice in the Description page of Project Settings.

#include "NobleArchimedesHUD.h"
#include "Blueprint/UserWidget.h"

ANobleArchimedesHUD::ANobleArchimedesHUD()
{
	CurrentHUDWidget = nullptr;
	CurrentMenuWidget = nullptr;
}

void ANobleArchimedesHUD::BeginPlay()
{
	Super::BeginPlay();

	// Show HUD by default on game start
	ShowHUD();
}

void ANobleArchimedesHUD::ShowHUD()
{
	if (HUDWidgetClass && !CurrentHUDWidget)
	{
		CurrentHUDWidget = CreateWidget<UUserWidget>(GetWorld(), HUDWidgetClass);
		if (CurrentHUDWidget)
		{
			CurrentHUDWidget->AddToViewport();
		}
	}
}

void ANobleArchimedesHUD::HideHUD()
{
	if (CurrentHUDWidget)
	{
		CurrentHUDWidget->RemoveFromParent();
		CurrentHUDWidget = nullptr;
	}
}

void ANobleArchimedesHUD::ShowMainMenu()
{
	if (MainMenuWidgetClass && !CurrentMenuWidget)
	{
		CurrentMenuWidget = CreateWidget<UUserWidget>(GetWorld(), MainMenuWidgetClass);
		if (CurrentMenuWidget)
		{
			CurrentMenuWidget->AddToViewport();
		}
	}
}

void ANobleArchimedesHUD::HideMainMenu()
{
	if (CurrentMenuWidget)
	{
		CurrentMenuWidget->RemoveFromParent();
		CurrentMenuWidget = nullptr;
	}
}

void ANobleArchimedesHUD::ShowPauseMenu()
{
	if (PauseMenuWidgetClass && !CurrentMenuWidget)
	{
		CurrentMenuWidget = CreateWidget<UUserWidget>(GetWorld(), PauseMenuWidgetClass);
		if (CurrentMenuWidget)
		{
			CurrentMenuWidget->AddToViewport();
		}
	}
}

void ANobleArchimedesHUD::HidePauseMenu()
{
	if (CurrentMenuWidget)
	{
		CurrentMenuWidget->RemoveFromParent();
		CurrentMenuWidget = nullptr;
	}
}

void ANobleArchimedesHUD::ShowSaveLoadMenu()
{
	if (SaveLoadWidgetClass && !CurrentMenuWidget)
	{
		CurrentMenuWidget = CreateWidget<UUserWidget>(GetWorld(), SaveLoadWidgetClass);
		if (CurrentMenuWidget)
		{
			CurrentMenuWidget->AddToViewport();
		}
	}
}

void ANobleArchimedesHUD::HideSaveLoadMenu()
{
	if (CurrentMenuWidget)
	{
		CurrentMenuWidget->RemoveFromParent();
		CurrentMenuWidget = nullptr;
	}
}

void ANobleArchimedesHUD::ShowWeaponForge()
{
	if (WeaponForgeWidgetClass && !CurrentMenuWidget)
	{
		CurrentMenuWidget = CreateWidget<UUserWidget>(GetWorld(), WeaponForgeWidgetClass);
		if (CurrentMenuWidget)
		{
			CurrentMenuWidget->AddToViewport();
		}
	}
}

void ANobleArchimedesHUD::HideWeaponForge()
{
	if (CurrentMenuWidget)
	{
		CurrentMenuWidget->RemoveFromParent();
		CurrentMenuWidget = nullptr;
	}
}

void ANobleArchimedesHUD::ShowInnocentDevilStatus()
{
	if (InnocentDevilStatusWidgetClass && !CurrentMenuWidget)
	{
		CurrentMenuWidget = CreateWidget<UUserWidget>(GetWorld(), InnocentDevilStatusWidgetClass);
		if (CurrentMenuWidget)
		{
			CurrentMenuWidget->AddToViewport();
		}
	}
}

void ANobleArchimedesHUD::HideInnocentDevilStatus()
{
	if (CurrentMenuWidget)
	{
		CurrentMenuWidget->RemoveFromParent();
		CurrentMenuWidget = nullptr;
	}
}

void ANobleArchimedesHUD::ShowComboCounter()
{
	if (ComboCounterWidgetClass && !CurrentHUDWidget)
	{
		CurrentHUDWidget = CreateWidget<UUserWidget>(GetWorld(), ComboCounterWidgetClass);
		if (CurrentHUDWidget)
		{
			CurrentHUDWidget->AddToViewport();
		}
	}
}

void ANobleArchimedesHUD::HideComboCounter()
{
	if (CurrentHUDWidget)
	{
		CurrentHUDWidget->RemoveFromParent();
		CurrentHUDWidget = nullptr;
	}
}
