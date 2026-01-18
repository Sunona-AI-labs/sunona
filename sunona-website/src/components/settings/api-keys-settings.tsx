/**
 * Enhanced API Keys Settings Component
 * 
 * FEATURES:
 * - Add ANY provider key you have
 * - Multiple keys per category supported
 * - ANY key in a category = No charges for that service
 * - Buy telephony from platform with wallet
 */
"use client";

import * as React from "react";
import {
    Key,
    Plus,
    Trash2,
    Check,
    X,
    AlertCircle,
    Eye,
    EyeOff,
    ExternalLink,
    Star,
    Phone,
    CreditCard,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
    useProviderKeysStore,
    PLATFORM_FEE_PER_MINUTE,
    PLATFORM_PROVIDER_COSTS,
    SUPPORTED_PROVIDERS,
    type ProviderType,
    type ProviderKey,
} from "@/lib/store/provider-keys-store";
import { useAuthStore, selectWallet } from "@/lib/store/auth-store";

// ============================================================
// Provider Key Row Component
// ============================================================

interface KeyRowProps {
    keyData: ProviderKey;
    providerName: string;
}

function KeyRow({ keyData, providerName }: KeyRowProps) {
    const { removeKey, setActiveKey } = useProviderKeysStore();
    const [showKey, setShowKey] = React.useState(false);

    return (
        <div className="flex items-center justify-between py-2 px-3 bg-gray-50 rounded-lg">
            <div className="flex items-center gap-3">
                {keyData.isActive && (
                    <Star className="w-4 h-4 text-amber-500 fill-amber-500" />
                )}
                <div>
                    <div className="flex items-center gap-2">
                        <span className="text-sm font-medium text-gray-900">{providerName}</span>
                        <Badge variant={keyData.isValid ? "success" : "error"} size="sm">
                            {keyData.isValid ? "Valid" : "Invalid"}
                        </Badge>
                    </div>
                    <span className="text-xs text-gray-500 font-mono">
                        {showKey ? keyData.apiKey : `${keyData.keyPrefix}${"•".repeat(16)}`}
                    </span>
                </div>
            </div>
            <div className="flex items-center gap-1">
                <button
                    onClick={() => setShowKey(!showKey)}
                    className="p-1.5 text-gray-400 hover:text-gray-600"
                >
                    {showKey ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
                {!keyData.isActive && (
                    <button
                        onClick={() => setActiveKey(keyData.id)}
                        className="p-1.5 text-amber-500 hover:text-amber-600"
                        title="Set as active"
                    >
                        <Star className="w-4 h-4" />
                    </button>
                )}
                <button
                    onClick={() => removeKey(keyData.id)}
                    className="p-1.5 text-red-400 hover:text-red-600"
                >
                    <Trash2 className="w-4 h-4" />
                </button>
            </div>
        </div>
    );
}

// ============================================================
// Add Key Modal
// ============================================================

interface AddKeyModalProps {
    type: ProviderType;
    onClose: () => void;
}

function AddKeyModal({ type, onClose }: AddKeyModalProps) {
    const { addKey } = useProviderKeysStore();
    const providers = SUPPORTED_PROVIDERS[type];

    const [selectedProvider, setSelectedProvider] = React.useState(providers[0].id);
    const [apiKey, setApiKey] = React.useState("");
    const [isAdding, setIsAdding] = React.useState(false);

    const handleAdd = async () => {
        if (!apiKey.trim()) return;
        setIsAdding(true);
        addKey(selectedProvider, type, apiKey);
        setIsAdding(false);
        onClose();
    };

    const selectedProviderData = providers.find((p) => p.id === selectedProvider);

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
            <div className="bg-white rounded-xl shadow-xl w-full max-w-md mx-4 p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                    Add {type.toUpperCase()} API Key
                </h3>

                {/* Provider Selection */}
                <div className="mb-4">
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                        Select Provider
                    </label>
                    <select
                        value={selectedProvider}
                        onChange={(e) => setSelectedProvider(e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                        {providers.map((p) => (
                            <option key={p.id} value={p.id}>
                                {p.name}
                            </option>
                        ))}
                    </select>
                </div>

                {/* API Key Input */}
                <div className="mb-4">
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                        API Key
                    </label>
                    <input
                        type="password"
                        value={apiKey}
                        onChange={(e) => setApiKey(e.target.value)}
                        placeholder={selectedProviderData?.placeholder || "Enter API key"}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                    {selectedProviderData?.docs && (
                        <a
                            href={selectedProviderData.docs}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="inline-flex items-center gap-1 text-xs text-blue-600 hover:text-blue-700 mt-2"
                        >
                            Get API key from {selectedProviderData.name}
                            <ExternalLink className="w-3 h-3" />
                        </a>
                    )}
                </div>

                {/* Info */}
                <div className="p-3 bg-green-50 border border-green-200 rounded-lg mb-4">
                    <p className="text-xs text-green-800">
                        ✅ Adding this key means <strong>no {type.toUpperCase()} charges</strong> -
                        you'll only pay our $0.01/min platform fee for this service!
                    </p>
                </div>

                {/* Actions */}
                <div className="flex justify-end gap-3">
                    <Button variant="ghost" onClick={onClose}>
                        Cancel
                    </Button>
                    <Button onClick={handleAdd} disabled={!apiKey.trim() || isAdding}>
                        {isAdding ? "Adding..." : "Add Key"}
                    </Button>
                </div>
            </div>
        </div>
    );
}

// ============================================================
// Provider Category Section
// ============================================================

interface CategorySectionProps {
    type: ProviderType;
    title: string;
    description: string;
}

function CategorySection({ type, title, description }: CategorySectionProps) {
    const { getKeysByType, hasAnyKeyForType } = useProviderKeysStore();
    const [showAddModal, setShowAddModal] = React.useState(false);

    const keys = getKeysByType(type);
    const hasKeys = hasAnyKeyForType(type);
    const providers = SUPPORTED_PROVIDERS[type];

    const getProviderName = (providerId: string) => {
        return providers.find((p) => p.id === providerId)?.name || providerId;
    };

    return (
        <Card className="bg-white border border-gray-200">
            <CardHeader className="pb-3">
                <div className="flex items-center justify-between">
                    <div>
                        <CardTitle className="text-base">{title}</CardTitle>
                        <p className="text-xs text-gray-500 mt-1">{description}</p>
                    </div>
                    <div className="flex items-center gap-2">
                        <Badge variant={hasKeys ? "success" : "default"} size="sm">
                            {hasKeys ? "BYOK Active" : "Using Platform"}
                        </Badge>
                        <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => setShowAddModal(true)}
                        >
                            <Plus className="w-4 h-4 mr-1" />
                            Add
                        </Button>
                    </div>
                </div>
            </CardHeader>
            <CardContent className="pt-0">
                {keys.length === 0 ? (
                    <div className="text-center py-4 text-sm text-gray-500">
                        <Key className="w-6 h-6 mx-auto mb-2 text-gray-300" />
                        No keys added. Using platform keys (${PLATFORM_PROVIDER_COSTS[type].toFixed(3)}/min)
                    </div>
                ) : (
                    <div className="space-y-2">
                        {keys.map((key) => (
                            <KeyRow
                                key={key.id}
                                keyData={key}
                                providerName={getProviderName(key.provider)}
                            />
                        ))}
                        <p className="text-xs text-green-600 mt-2">
                            ✅ No {type.toUpperCase()} charges - using your keys!
                        </p>
                    </div>
                )}
            </CardContent>

            {showAddModal && (
                <AddKeyModal type={type} onClose={() => setShowAddModal(false)} />
            )}
        </Card>
    );
}

// ============================================================
// Telephony Purchase Section
// ============================================================

function TelephonyPurchaseSection() {
    const wallet = useAuthStore(selectWallet);

    const phoneNumberPlans = [
        { type: "local", price: 1.00, description: "US Local Number", monthly: 1.00 },
        { type: "toll_free", price: 2.00, description: "US Toll-Free (800)", monthly: 2.50 },
        { type: "mobile", price: 1.50, description: "Mobile Number", monthly: 1.50 },
    ];

    return (
        <Card className="bg-gradient-to-r from-purple-50 to-pink-50 border-purple-200">
            <CardHeader className="pb-3">
                <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                        <Phone className="w-5 h-5 text-purple-600" />
                        <CardTitle className="text-base">Buy Phone Numbers</CardTitle>
                    </div>
                    <Badge variant="purple" size="sm">
                        Balance: ${wallet?.balance?.toFixed(2) || "0.00"}
                    </Badge>
                </div>
                <p className="text-xs text-gray-600 mt-1">
                    Purchase phone numbers directly from our platform using your wallet
                </p>
            </CardHeader>
            <CardContent className="pt-0">
                <div className="space-y-2">
                    {phoneNumberPlans.map((plan) => (
                        <div
                            key={plan.type}
                            className="flex items-center justify-between p-3 bg-white rounded-lg border border-gray-200"
                        >
                            <div>
                                <span className="text-sm font-medium text-gray-900">
                                    {plan.description}
                                </span>
                                <p className="text-xs text-gray-500">
                                    ${plan.monthly}/month after purchase
                                </p>
                            </div>
                            <Button
                                size="sm"
                                disabled={!wallet || wallet.balance < plan.price}
                            >
                                <CreditCard className="w-4 h-4 mr-1" />
                                ${plan.price}
                            </Button>
                        </div>
                    ))}
                </div>
                <p className="text-xs text-gray-500 mt-3 text-center">
                    No telephony API key needed - numbers are managed by Sunona
                </p>
            </CardContent>
        </Card>
    );
}

// ============================================================
// Main Component
// ============================================================

export function ApiKeysSettings() {
    const { getEstimatedCostPerMinute, getTotalKeyCount, getBillingMode } = useProviderKeysStore();
    const estimatedCost = getEstimatedCostPerMinute();
    const totalKeys = getTotalKeyCount();
    const billingMode = getBillingMode();

    const byokCount = [
        billingMode.llm === "byok",
        billingMode.stt === "byok",
        billingMode.tts === "byok",
        billingMode.telephony === "byok",
    ].filter(Boolean).length;

    return (
        <div className="space-y-6">
            {/* Summary Card */}
            <Card className="bg-gradient-to-r from-blue-50 to-cyan-50 border-blue-200">
                <CardContent className="p-6">
                    <div className="flex items-start justify-between">
                        <div>
                            <h3 className="text-lg font-semibold text-gray-900">
                                Your Billing Summary
                            </h3>
                            <p className="text-sm text-gray-600 mt-1">
                                {totalKeys > 0
                                    ? `${totalKeys} API keys added • ${byokCount}/4 services using BYOK`
                                    : "Add your API keys to save on provider costs!"}
                            </p>
                        </div>
                        <div className="text-right">
                            <div className="text-2xl font-bold text-gray-900">
                                ${estimatedCost.toFixed(3)}
                                <span className="text-sm font-normal text-gray-500">/min</span>
                            </div>
                            <p className="text-xs text-gray-500">Estimated cost</p>
                        </div>
                    </div>

                    {/* Cost Breakdown */}
                    <div className="mt-4 pt-4 border-t border-blue-200">
                        <div className="grid grid-cols-5 gap-2 text-center text-xs">
                            <div className="p-2 bg-white/60 rounded-lg">
                                <div className="text-gray-500">Platform</div>
                                <div className="font-mono font-medium text-green-600">
                                    ${PLATFORM_FEE_PER_MINUTE.toFixed(3)}
                                </div>
                            </div>
                            {(["llm", "stt", "tts", "telephony"] as const).map((type) => (
                                <div key={type} className="p-2 bg-white/60 rounded-lg">
                                    <div className="text-gray-500 uppercase">{type}</div>
                                    <div className={`font-mono font-medium ${billingMode[type] === "byok" ? "text-green-600" : "text-gray-700"
                                        }`}>
                                        {billingMode[type] === "byok" ? "FREE" : `$${PLATFORM_PROVIDER_COSTS[type].toFixed(3)}`}
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                </CardContent>
            </Card>

            {/* Info Banner */}
            <div className="flex items-start gap-3 p-4 bg-amber-50 border border-amber-200 rounded-lg">
                <AlertCircle className="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" />
                <div>
                    <p className="text-sm text-amber-800 font-medium">
                        Bring Your Own Keys (BYOK) - Add Any Provider!
                    </p>
                    <p className="text-xs text-amber-700 mt-1">
                        Add <strong>any API key</strong> you have. If you add even ONE key for a service
                        (e.g., any LLM key), we won't charge you for that service - only the
                        <strong> $0.01/min platform fee</strong>!
                    </p>
                </div>
            </div>

            {/* Provider Categories */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <CategorySection
                    type="llm"
                    title="Language Models (LLM)"
                    description="OpenAI, Anthropic, Groq, Mistral, and more"
                />
                <CategorySection
                    type="stt"
                    title="Speech-to-Text (STT)"
                    description="Deepgram, AssemblyAI, Whisper, and more"
                />
                <CategorySection
                    type="tts"
                    title="Text-to-Speech (TTS)"
                    description="ElevenLabs, Cartesia, PlayHT, and more"
                />
                <CategorySection
                    type="telephony"
                    title="Telephony"
                    description="Twilio, Plivo, Vonage, Telnyx, and more"
                />
            </div>

            {/* Telephony Purchase */}
            <TelephonyPurchaseSection />
        </div>
    );
}
