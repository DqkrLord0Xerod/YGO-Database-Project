// yugioh_db_generator/web/static/js/components/DeckAnalyzer.jsx
const DeckAnalyzer = () => {
    const [deckInput, setDeckInput] = React.useState('');
    const [loading, setLoading] = React.useState(false);
    const [activeTab, setActiveTab] = React.useState('input');
    const [deckData, setDeckData] = React.useState(null);
    const [analysis, setAnalysis] = React.useState(null);
    const [cardData, setCardData] = React.useState({});
    const [error, setError] = React.useState(null);

    const handleInputChange = (e) => {
        setDeckInput(e.target.value);
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError(null);

        try {
            // Parse the deck locally for visualization
            const { mainDeck, extraDeck } = parseDeckList(deckInput);
            setDeckData({ mainDeck, extraDeck });

            // Call API for analysis
            const response = await fetch('/api/analyze-deck', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ deckList: deckInput }),
            });

            const data = await response.json();

            if (data.success) {
                setAnalysis(data.analysis);
                setCardData(data.card_data || {});
                setActiveTab('visualization');
            } else {
                setError(data.error || 'An error occurred during analysis');
            }
        } catch (err) {
            setError('Failed to analyze deck: ' + err.message);
        } finally {
            setLoading(false);
        }
    };

    const parseDeckList = (input) => {
        const lines = input.split('\n');
        let mainDeck = [];
        let extraDeck = [];
        let currentSection = 'main';

        for (const line of lines) {
            const trimmed = line.trim();
            if (!trimmed || trimmed.startsWith('#')) {
                if (trimmed.toLowerCase().includes('extra deck')) {
                    currentSection = 'extra';
                }
                continue;
            }

            if (currentSection === 'main') {
                mainDeck.push(trimmed);
            } else {
                extraDeck.push(trimmed);
            }
        }

        return { mainDeck, extraDeck };
    };

    const loadExampleDeck = () => {
        const exampleDeck = `# Main Deck
Snake-eye Flamberge Dragon
Snake-eye Diabellstar
Snake-eye Ash
Snake-eye Oak
Snake-eye Poplar
Snake-eye Birch
Divine Temple of the Snake-eyes
One for One
Called by the Grave
Triple Tactics Thrust
Triple Tactics Talents
Infinite Impermanence

# Extra Deck
Snake-eye Doomed Dragon
Infernal Flame Banshee
I:P Masquerena
Relinquished Anima
Cross-Sheep`;

        setDeckInput(exampleDeck);
    };

    return (
        <div>
            {/* Navigation Tabs */}
            <ul className="nav nav-tabs mb-3">
                <li className="nav-item">
                    <button
                        className={`nav-link ${activeTab === 'input' ? 'active' : ''}`}
                        onClick={() => setActiveTab('input')}
                    >
                        Deck Input
                    </button>
                </li>
                <li className="nav-item">
                    <button
                        className={`nav-link ${activeTab === 'visualization' ? 'active' : ''}`}
                        onClick={() => setActiveTab('visualization')}
                        disabled={!deckData}
                    >
                        Visualization
                    </button>
                </li>
                <li className="nav-item">
                    <button
                        className={`nav-link ${activeTab === 'analysis' ? 'active' : ''}`}
                        onClick={() => setActiveTab('analysis')}
                        disabled={!analysis}
                    >
                        Analysis
                    </button>
                </li>
            </ul>

            {/* Error Alert */}
            {error && (
                <div className="alert alert-danger" role="alert">
                    {error}
                </div>
            )}

            {/* Tab Content */}
            <div className="tab-content">
                {activeTab === 'input' && (
                    <div>
                        <form onSubmit={handleSubmit}>
                            <div className="mb-3">
                                <label htmlFor="deckList" className="form-label">Enter your decklist (one card per line):</label>
                                <textarea
                                    id="deckList"
                                    className="form-control font-monospace"
                                    rows="15"
                                    value={deckInput}
                                    onChange={handleInputChange}
                                    placeholder="# Main Deck&#10;Dark Magician&#10;Blue-Eyes White Dragon&#10;&#10;# Extra Deck&#10;Stardust Dragon"
                                    required
                                ></textarea>
                            </div>
                            <div className="d-flex justify-content-between">
                                <button
                                    type="button"
                                    className="btn btn-secondary"
                                    onClick={loadExampleDeck}
                                >
                                    Load Example Deck
                                </button>
                                <button
                                    type="submit"
                                    className="btn btn-primary"
                                    disabled={loading}
                                >
                                    {loading ? (
                                        <>
                                            <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                                            Analyzing...
                                        </>
                                    ) : 'Analyze Deck'}
                                </button>
                            </div>
                        </form>
                    </div>
                )}

                {activeTab === 'visualization' && deckData && (
                    <DeckVisualization deckData={deckData} cardData={cardData} />
                )}

                {activeTab === 'analysis' && analysis && (
                    <AnalysisResults analysis={analysis} />
                )}
            </div>
        </div>
    );
};