// Copyright Epic Games, Inc. All Rights Reserved.

#include "NobleArchimedesEditor.h"

#include "Modules/ModuleManager.h"

DEFINE_LOG_CATEGORY_STATIC(LogNobleEditor, Log, All);

void FNobleArchimedesEditorModule::StartupModule()
{
	UE_LOG(LogNobleEditor, Log, TEXT("NobleArchimedesEditor module started."));
}

void FNobleArchimedesEditorModule::ShutdownModule()
{
	UE_LOG(LogNobleEditor, Log, TEXT("NobleArchimedesEditor module shut down."));
}

IMPLEMENT_MODULE(FNobleArchimedesEditorModule, NobleArchimedesEditor)
