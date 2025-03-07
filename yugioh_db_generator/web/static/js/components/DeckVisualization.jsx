// yugioh_db_generator/web/static/js/components/DeckVisualization.jsx
const DeckVisualization = ({ deckData, cardData }) => {
    const getCardTypeColors = (cardName) => {
        const card = cardData[cardName] || {};
        const cardType = (card.type || '').toLowerCase();

        // Default colors
        let colors = { borderColor: '#444', bgColor: '#ddd' };

        // Determine card type and set colors
        if (cardType.includes('monster')) {
            if (cardType.includes('normal')) {
                colors = { borderColor: '#8B6914', bgColor: '#DEB887' };
            } else if (cardType.includes('effect')) {
                colors = { borderColor: '#8B4513', bgColor: '#D2691E' };
            } else if (cardType.includes('ritual')) {
                colors = { borderColor: '#191970', bgColor: '#4169E1' };
            } else if (cardType.includes('fusion')) {
                colors = { borderColor: '#551A8B', bgColor: '#9370DB' };
            } else if (cardType.includes('synchro')) {
                colors = { borderColor: '#808080', bgColor: '#FFFFFF' };
            } else if (cardType.includes('xyz')) {
                colors = { borderColor: '#000', bgColor: '#333' };
            } else if (cardType.includes('link')) {
                colors = { borderColor: '#00008B', bgColor: '#1E90FF' };
            } else if (cardType.includes('pendulum')) {
                colors = { borderColor: '#008000', bgColor: '#98FB98' };
            } else {
                colors = { borderColor: '#8B4513', bgColor: '#D2691E' }; // Default to effect monster
            }
        } else if (cardType.includes('spell')) {
            colors = { borderColor: '#006400', bgColor: '#98FB98' };
        } else if (cardType.includes('trap')) {
            colors = { borderColor: '#8B008B', bgColor: '#FF69B4' };
        }

        return colors;
    };

    // Count cards and create object with counts
    const countCards = (deckSection) => {
        const counts = {};
        deckSection.forEach(card => {
            counts[card] = (counts[card] || 0) + 1;
        });
        return counts;
    };

    const mainDeckCounts = countCards(deckData.mainDeck);
    const extraDeckCounts = countCards(deckData.extraDeck);

    // Count card types
    const countCardTypes = () => {
        const counts = {
            monsters: 0,
            spells: 0,
            traps: 0,
            fusion: 0,
            synchro: 0,
            xyz: 0,
            link: 0
        };

        // Process main deck
        Object.keys(mainDeckCounts).forEach(cardName => {
            const card = cardData[cardName] || {};
            const cardType = (card.type || '').toLowerCase();
            const count = mainDeckCounts[cardName];

            if (cardType.includes('monster')) {
                counts.monsters += count;
            } else if (cardType.includes('spell')) {
                counts.spells += count;
            } else if (cardType.includes('trap')) {
                counts.traps += count;
            }
        });

        // Process extra deck
        Object.keys(extraDeckCounts).forEach(cardName => {
            const card = cardData[cardName] || {};
            const cardType = (card.type || '').toLowerCase();
            const count = extraDeckCounts[cardName];

            if (cardType.includes('fusion')) {
                counts.fusion += count;
            } else if (cardType.includes('synchro')) {
                counts.synchro += count;
            } else if (cardType.includes('xyz')) {
                counts.xyz += count;
            } else if (cardType.includes('link')) {
                counts.link += count;
            }
        });

        return counts;
    };

    const cardTypes = countCardTypes();

    return (
        <div>
            {/* Main Deck */}
            <div className="deck-section">
                <div className="deck-section-header">
                    <h3>Main Deck: {deckData.mainDeck.length}</h3>
                    <span>
                        Monster: {cardTypes.monsters} |
                        Spell: {cardTypes.spells} |
                        Trap: {cardTypes.traps}
                    </span>
                </div>
                <div className="card-grid">
                    {Object.entries(mainDeckCounts).map(([cardName, count]) => {
                        const colors = getCardTypeColors(cardName);
                        return (
                            <div
                                key={cardName}
                                className="card-container"
                                style={{
                                    borderLeft: `5px solid ${colors.borderColor}`,
                                    backgroundColor: colors.bgColor
                                }}
                                title={cardName}
                                onClick={() => setSelectedCard(cardName)}
                            >
                                <div className="card-image-container">
                                    <img
                                        src={`https://images.ygoprodeck.com/images/cards_small/${cardData[cardName]?.id || cardName.replace(/[^a-zA-Z0-9]/g, '')}.jpg`}
                                        alt={cardName}
                                        className="card-image"
                                        onError={(e) => {
                                            e.target.onerror = null;
                                            e.target.src = "https://via.placeholder.com/90x130?text=No+Image";
                                        }}
                                    />
                                </div>
                                <div className="card-info">
                                    <div className="fw-bold text-truncate small">{cardName}</div>
                                </div>
                                {count > 1 && <div className="card-count">{count}</div>}
                            </div>
                        );
                    })}
                </div>
            </div>

            {/* Extra Deck */}
            {deckData.extraDeck.length > 0 && (
                <div className="deck-section">
                    <div className="deck-section-header">
                        <h3>Extra Deck: {deckData.extraDeck.length}</h3>
                        <span>
                            Fusion: {cardTypes.fusion} |
                            Synchro: {cardTypes.synchro} |
                            Xyz: {cardTypes.xyz} |
                            Link: {cardTypes.link}
                        </span>
                    </div>
                    <div className="card-grid">
                        {Object.entries(extraDeckCounts).map(([cardName, count]) => {
                            const colors = getCardTypeColors(cardName);
                            return (
                                <div
                                    key={cardName}
                                    className="card-container"
                                    style={{
                                        borderLeft: `5px solid ${colors.borderColor}`,
                                        backgroundColor: colors.bgColor
                                    }}
                                    title={cardName}
                                >
                                    <div className="p-2">
                                        <div className="fw-bold text-truncate">{cardName}</div>
                                        <div className="small text-muted">
                                            {cardData[cardName]?.type || 'Unknown'}
                                        </div>
                                    </div>
                                    {count > 1 && <div className="card-count">{count}</div>}
                                </div>
                            );
                        })}
                    </div>
                </div>
            )}
        </div>
    );
};