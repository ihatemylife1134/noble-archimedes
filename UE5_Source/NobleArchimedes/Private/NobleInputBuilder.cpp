// Fill out your copyright notice in the Description page of Project Settings.

#include "NobleInputBuilder.h"
#include "InputAction.h"
#include "InputMappingContext.h"
#include "InputModifiers.h"

void UNobleInputBuilder::AddKeyMapping(UInputMappingContext* Context, UInputAction* Action, FName KeyName,
	bool bNegateX, bool bNegateY, bool bSwizzleYXZ)
{
	if (!Context || !Action || KeyName.IsNone())
	{
		return;
	}

	const FKey Key(KeyName);
	if (!Key.IsValid())
	{
		UE_LOG(LogTemp, Warning, TEXT("NobleInputBuilder: unknown key '%s'"), *KeyName.ToString());
		return;
	}

	FEnhancedActionKeyMapping& Mapping = Context->MapKey(Action, Key);

	if (bSwizzleYXZ)
	{
		UInputModifierSwizzleAxis* Swizzle = NewObject<UInputModifierSwizzleAxis>(Context);
		Swizzle->Order = EInputAxisSwizzle::YXZ;
		Mapping.Modifiers.Add(Swizzle);
	}

	if (bNegateX || bNegateY)
	{
		UInputModifierNegate* Negate = NewObject<UInputModifierNegate>(Context);
		Negate->bX = bNegateX;
		Negate->bY = bNegateY;
		Negate->bZ = false;
		Mapping.Modifiers.Add(Negate);
	}

	Context->MarkPackageDirty();
}

void UNobleInputBuilder::ClearMappings(UInputMappingContext* Context)
{
	if (!Context)
	{
		return;
	}

	Context->UnmapAll();
	Context->MarkPackageDirty();
}
