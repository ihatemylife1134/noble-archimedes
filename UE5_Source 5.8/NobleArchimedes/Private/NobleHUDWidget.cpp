// Fill out your copyright notice in the Description page of Project Settings.

#include "NobleHUDWidget.h"
#include "HectorCharacter.h"
#include "NobleArchimedesGameModeBase.h"
#include "Blueprint/WidgetTree.h"
#include "Engine/World.h"
#include "Components/CanvasPanel.h"
#include "Components/CanvasPanelSlot.h"
#include "Components/ProgressBar.h"
#include "Components/TextBlock.h"
#include "Styling/SlateColor.h"

void UNobleHUDWidget::NativeOnInitialized()
{
	Super::NativeOnInitialized();
	BuildLayout();
}

void UNobleHUDWidget::BuildLayout()
{
	if (!WidgetTree || WidgetTree->RootWidget)
	{
		return;
	}

	UCanvasPanel* Root = WidgetTree->ConstructWidget<UCanvasPanel>(UCanvasPanel::StaticClass(), TEXT("RootCanvas"));
	if (!Root)
	{
		return;
	}
	WidgetTree->RootWidget = Root;
	UE_LOG(LogTemp, Log, TEXT("NobleArchimedes: HUD widget layout built."));

	// Health bar (top-left).
	HealthBar = WidgetTree->ConstructWidget<UProgressBar>(UProgressBar::StaticClass(), TEXT("HealthBar"));
	HealthBar->SetPercent(1.0f);
	HealthBar->SetFillColorAndOpacity(FLinearColor(0.55f, 0.04f, 0.04f, 1.0f));
	if (UCanvasPanelSlot* CanvasSlot = Root->AddChildToCanvas(HealthBar))
	{
		CanvasSlot->SetAnchors(FAnchors(0.0f, 0.0f));
		CanvasSlot->SetPosition(FVector2D(32.0f, 36.0f));
		CanvasSlot->SetSize(FVector2D(340.0f, 20.0f));
		CanvasSlot->SetZOrder(10);
	}

	HealthText = WidgetTree->ConstructWidget<UTextBlock>(UTextBlock::StaticClass(), TEXT("HealthText"));
	HealthText->SetText(FText::FromString(TEXT("HP 100 / 100")));
	HealthText->SetColorAndOpacity(FSlateColor(FLinearColor::White));
	HealthText->SetShadowOffset(FVector2D(1.0f, 1.0f));
	HealthText->SetShadowColorAndOpacity(FLinearColor::Black);
	if (UCanvasPanelSlot* CanvasSlot = Root->AddChildToCanvas(HealthText))
	{
		CanvasSlot->SetAnchors(FAnchors(0.0f, 0.0f));
		CanvasSlot->SetPosition(FVector2D(36.0f, 34.0f));
		CanvasSlot->SetSize(FVector2D(340.0f, 24.0f));
		CanvasSlot->SetZOrder(11);
	}

	// Mana bar (below health).
	ManaBar = WidgetTree->ConstructWidget<UProgressBar>(UProgressBar::StaticClass(), TEXT("ManaBar"));
	ManaBar->SetPercent(1.0f);
	ManaBar->SetFillColorAndOpacity(FLinearColor(0.05f, 0.2f, 0.65f, 1.0f));
	if (UCanvasPanelSlot* CanvasSlot = Root->AddChildToCanvas(ManaBar))
	{
		CanvasSlot->SetAnchors(FAnchors(0.0f, 0.0f));
		CanvasSlot->SetPosition(FVector2D(32.0f, 68.0f));
		CanvasSlot->SetSize(FVector2D(270.0f, 14.0f));
		CanvasSlot->SetZOrder(10);
	}

	ManaText = WidgetTree->ConstructWidget<UTextBlock>(UTextBlock::StaticClass(), TEXT("ManaText"));
	ManaText->SetText(FText::FromString(TEXT("MP 100 / 100")));
	ManaText->SetColorAndOpacity(FSlateColor(FLinearColor(0.85f, 0.9f, 1.0f)));
	ManaText->SetShadowOffset(FVector2D(1.0f, 1.0f));
	ManaText->SetShadowColorAndOpacity(FLinearColor::Black);
	if (UCanvasPanelSlot* CanvasSlot = Root->AddChildToCanvas(ManaText))
	{
		CanvasSlot->SetAnchors(FAnchors(0.0f, 0.0f));
		CanvasSlot->SetPosition(FVector2D(36.0f, 64.0f));
		CanvasSlot->SetSize(FVector2D(270.0f, 22.0f));
		CanvasSlot->SetZOrder(11);
	}

	// Level / chapter / weapon (top-right).
	StatusText = WidgetTree->ConstructWidget<UTextBlock>(UTextBlock::StaticClass(), TEXT("StatusText"));
	StatusText->SetText(FText::FromString(TEXT("Lv 1   Chapter 1")));
	StatusText->SetJustification(ETextJustify::Right);
	StatusText->SetColorAndOpacity(FSlateColor(FLinearColor(0.95f, 0.9f, 0.75f)));
	StatusText->SetShadowOffset(FVector2D(1.0f, 1.0f));
	StatusText->SetShadowColorAndOpacity(FLinearColor::Black);
	if (UCanvasPanelSlot* CanvasSlot = Root->AddChildToCanvas(StatusText))
	{
		CanvasSlot->SetAnchors(FAnchors(1.0f, 0.0f));
		CanvasSlot->SetAlignment(FVector2D(1.0f, 0.0f));
		CanvasSlot->SetPosition(FVector2D(-32.0f, 32.0f));
		CanvasSlot->SetSize(FVector2D(420.0f, 72.0f));
		CanvasSlot->SetZOrder(10);
	}

	// Controls hint (bottom-centre).
	HintText = WidgetTree->ConstructWidget<UTextBlock>(UTextBlock::StaticClass(), TEXT("HintText"));
	HintText->SetText(FText::FromString(
		TEXT("WASD Move | Mouse Look | LMB Attack | RMB Heavy | Shift Dodge | Ctrl Guard | E Interact | Q Devil")));
	HintText->SetJustification(ETextJustify::Center);
	HintText->SetColorAndOpacity(FSlateColor(FLinearColor(0.8f, 0.8f, 0.8f, 0.9f)));
	HintText->SetShadowOffset(FVector2D(1.0f, 1.0f));
	HintText->SetShadowColorAndOpacity(FLinearColor::Black);
	if (UCanvasPanelSlot* CanvasSlot = Root->AddChildToCanvas(HintText))
	{
		CanvasSlot->SetAnchors(FAnchors(0.5f, 1.0f));
		CanvasSlot->SetAlignment(FVector2D(0.5f, 1.0f));
		CanvasSlot->SetPosition(FVector2D(0.0f, -20.0f));
		CanvasSlot->SetSize(FVector2D(1100.0f, 26.0f));
		CanvasSlot->SetZOrder(10);
	}
}

void UNobleHUDWidget::NativeTick(const FGeometry& MyGeometry, float InDeltaTime)
{
	Super::NativeTick(MyGeometry, InDeltaTime);

	AHectorCharacter* Hector = Cast<AHectorCharacter>(GetOwningPlayerPawn());
	if (!Hector)
	{
		return;
	}

	const float Health = Hector->GetHealth();
	const float MaxHealth = FMath::Max(1.0f, Hector->GetMaxHealth());
	const float Mana = Hector->GetMana();
	const float MaxMana = FMath::Max(1.0f, Hector->GetMaxMana());

	if (HealthBar)
	{
		HealthBar->SetPercent(FMath::Clamp(Health / MaxHealth, 0.0f, 1.0f));
	}
	if (HealthText)
	{
		HealthText->SetText(FText::FromString(
			FString::Printf(TEXT("HP %.0f / %.0f"), Health, MaxHealth)));
	}
	if (ManaBar)
	{
		ManaBar->SetPercent(FMath::Clamp(Mana / MaxMana, 0.0f, 1.0f));
	}
	if (ManaText)
	{
		ManaText->SetText(FText::FromString(
			FString::Printf(TEXT("MP %.0f / %.0f"), Mana, MaxMana)));
	}

	int32 Chapter = 1;
	if (const UWorld* World = GetWorld())
	{
		if (const ANobleArchimedesGameModeBase* GameMode =
			World->GetAuthGameMode<ANobleArchimedesGameModeBase>())
		{
			Chapter = GameMode->GetCurrentChapter();
		}
	}

	if (StatusText)
	{
		const FString WeaponName = StaticEnum<EWeaponType>()->GetNameStringByValue(
			static_cast<int64>(Hector->GetEquippedWeaponType()));
		StatusText->SetText(FText::FromString(FString::Printf(
			TEXT("Lv %d   Chapter %d\n%s"),
			Hector->GetCharacterLevel(), Chapter, *WeaponName)));
	}
}
