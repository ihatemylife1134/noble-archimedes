// Copyright Epic Games, Inc. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "Modules/ModuleManager.h"

/**
 * Editor-only module for Noble Archimedes.
 *
 * Exists so tooling can author Animation Blueprint state machines, which is not
 * possible from the Python API (the state machine graph exposes its nodes only
 * to C++).
 */
class FNobleArchimedesEditorModule : public IModuleInterface
{
public:
	virtual void StartupModule() override;
	virtual void ShutdownModule() override;
};
