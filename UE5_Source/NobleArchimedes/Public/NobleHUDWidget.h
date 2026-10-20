// Fill out your copyright notice in the Description page of Project Settings.

#pragma once

#include "CoreMinimal.h"
#include "Blueprint/UserWidget.h"
#include "NobleHUDWidget.generated.h"

class UProgressBar;
class UTextBlock;

/**
 * C++ HUD layout used until the final UMG widgets are authored.
 *
 * It builds its own widget tree so the game has a readable HUD without
 * depending on a Widget Blueprint asset. A WBP subclass can replace the
 * visuals later without touching the HUD plumbing.
 */
UCLASS()
class NOBLEARCHIMEDES_API UNobleHUDWidget : public UUserWidget
{
	GENERATED_BODY()

public:
	virtual void NativeOnInitialized() override;
	virtual void NativeTick(const FGeometry& MyGeometry, float InDeltaTime) override;

protected:
	void BuildLayout();

	UPROPERTY()
	TObjectPtr<UProgressBar> HealthBar;

	UPROPERTY()
	TObjectPtr<UProgressBar> ManaBar;

	UPROPERTY()
	TObjectPtr<UTextBlock> HealthText;

	UPROPERTY()
	TObjectPtr<UTextBlock> ManaText;

	UPROPERTY()
	TObjectPtr<UTextBlock> StatusText;

	UPROPERTY()
	TObjectPtr<UTextBlock> HintText;
};
