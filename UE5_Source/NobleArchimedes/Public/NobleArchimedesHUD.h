// Fill out your copyright notice in the Description page of Project Settings.

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/HUD.h"
#include "NobleArchimedesHUD.generated.h"

/**
 * HUD class for Noble Archimedes
 * Provides C++ foundation for UMG widget Blueprints
 */
UCLASS()
class NOBLEARCHIMEDES_API ANobleArchimedesHUD : public AHUD
{
	GENERATED_BODY()

public:
	ANobleArchimedesHUD();

protected:
	virtual void BeginPlay() override;

public:
	//=============================================================================
	// HUD WIDGET REFERENCES
	//=============================================================================

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "HUD")
	TSubclassOf<class UUserWidget> HUDWidgetClass;

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "HUD")
	TSubclassOf<class UUserWidget> MainMenuWidgetClass;

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "HUD")
	TSubclassOf<class UUserWidget> PauseMenuWidgetClass;

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "HUD")
	TSubclassOf<class UUserWidget> SaveLoadWidgetClass;

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "HUD")
	TSubclassOf<class UUserWidget> WeaponForgeWidgetClass;

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "HUD")
	TSubclassOf<class UUserWidget> InnocentDevilStatusWidgetClass;

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "HUD")
	TSubclassOf<class UUserWidget> ComboCounterWidgetClass;

	//=============================================================================
	// WIDGET INSTANCES
	//=============================================================================

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "HUD")
	class UUserWidget* CurrentHUDWidget;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "HUD")
	class UUserWidget* CurrentMenuWidget;

	//=============================================================================
	// HUD ACTIONS
	//=============================================================================

	UFUNCTION(BlueprintCallable, Category = "HUD")
	void ShowHUD();

	UFUNCTION(BlueprintCallable, Category = "HUD")
	void HideHUD();

	UFUNCTION(BlueprintCallable, Category = "HUD")
	void ShowMainMenu();

	UFUNCTION(BlueprintCallable, Category = "HUD")
	void HideMainMenu();

	UFUNCTION(BlueprintCallable, Category = "HUD")
	void ShowPauseMenu();

	UFUNCTION(BlueprintCallable, Category = "HUD")
	void HidePauseMenu();

	UFUNCTION(BlueprintCallable, Category = "HUD")
	void ShowSaveLoadMenu();

	UFUNCTION(BlueprintCallable, Category = "HUD")
	void HideSaveLoadMenu();

	UFUNCTION(BlueprintCallable, Category = "HUD")
	void ShowWeaponForge();

	UFUNCTION(BlueprintCallable, Category = "HUD")
	void HideWeaponForge();

	UFUNCTION(BlueprintCallable, Category = "HUD")
	void ShowInnocentDevilStatus();

	UFUNCTION(BlueprintCallable, Category = "HUD")
	void HideInnocentDevilStatus();

	UFUNCTION(BlueprintCallable, Category = "HUD")
	void ShowComboCounter();

	UFUNCTION(BlueprintCallable, Category = "HUD")
	void HideComboCounter();
};
