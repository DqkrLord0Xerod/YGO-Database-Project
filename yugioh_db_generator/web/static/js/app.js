// yugioh_db_generator/web/static/js/app.js
const App = () => {
    return (
        <div className="mb-5">
            <h1 className="text-center mb-4">Yu-Gi-Oh! Deck Analyzer</h1>
            <p className="text-center text-muted mb-4">
                Analyze your Yu-Gi-Oh! deck for strengths, weaknesses and recommended improvements
            </p>
            <DeckAnalyzer />
        </div>
    );
};

// Add a new CardDetails component for card popups
// yugioh_db_generator/web/static/js/components/CardDetails.jsx
const CardDetails = ({ cardName, onClose }) => {
    const [loading, setLoading] = React.useState(true);
    const [cardInfo, setCardInfo] = React.useState(null);
    const [error, setError] = React.useState(null);

    React.useEffect(() => {
        const fetchCardDetails = async () => {
            try {
                setLoading(true);
                const response = await fetch(`/api/card-details/${encodeURIComponent(cardName)}`);
                const data = await response.json();
                
                if (data.success) {
                    setCardInfo(data);
                } else {
                    setError(data.error || 'Failed to fetch card details');
                }
            } catch (err) {
                setError(`Error: ${err.message}`);
            } finally {
                setLoading(false);
            }
        };
        
        fetchCardDetails();
    }, [cardName]);

    if (loading) {
        return (
            <div className="modal-dialog modal-lg">
                <div className="modal-content">
                    <div className="modal-header">
                        <h5 className="modal-title">{cardName}</h5>
                        <button type="button" className="btn-close" onClick={onClose}></button>
                    </div>
                    <div className="modal-body text-center py-5">
                        <div className="spinner-border text-primary" role="status">
                            <span className="visually-hidden">Loading...</span>
                        </div>
                        <p className="mt-3">Loading card details...</p>
                    </div>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="modal-dialog">
                <div className="modal-content">
                    <div className="modal-header">
                        <h5 className="modal-title">Error</h5>
                        <button type="button" className="btn-close" onClick={onClose}></button>
                    </div>
                    <div className="modal-body">
                        <div className="alert alert-danger">{error}</div>
                    </div>
                </div>
            </div>
        );
    }

    const card = cardInfo?.card || {};
    const rulings = cardInfo?.rulings || [];

    return (
        <div className="modal-dialog modal-lg">
            <div className="modal-content">
                <div className="modal-header">
                    <h5 className="modal-title">{card.name}</h5>
                    <button type="button" className="btn-close" onClick={onClose}></button>
                </div>
                <div className="modal-body">
                    <div className="row">
                        <div className="col-md-4">
                            <div className="text-center mb-3">
                                <img 
                                    src={`https://ygoprodeck.com/pics/${card.name?.replace(/ /g, '%20')}.jpg`}
                                    alt={card.name}
                                    className="img-fluid rounded"
                                    style={{ maxHeight: '300px' }}
                                    onError={(e) => {
                                        e.target.onerror = null;
                                        e.target.src = "https://via.placeholder.com/200x290?text=No+Image";
                                    }}
                                />
                            </div>
                        </div>
                        <div className="col-md-8">
                            <h4>Card Information</h4>
                            <table className="table table-sm">
                                <tbody>
                                    <tr>
                                        <th>Type:</th>
                                        <td>{card.type}</td>
                                    </tr>
                                    {card.attribute && (
                                        <tr>
                                            <th>Attribute:</th>
                                            <td>{card.attribute}</td>
                                        </tr>
                                    )}
                                    {card.level && (
                                        <tr>
                                            <th>Level/Rank:</th>
                                            <td>{card.level}</td>
                                        </tr>
                                    )}
                                    {card.race && (
                                        <tr>
                                            <th>Race:</th>
                                            <td>{card.race}</td>
                                        </tr>
                                    )}
                                    {card.atk !== undefined && (
                                        <tr>
                                            <th>ATK/DEF:</th>
                                            <td>{card.atk} / {card.def}</td>
                                        </tr>
                                    )}
                                </tbody>
                            </table>
                            <div className="card mb-3">
                                <div className="card-header">Description</div>
                                <div className="card-body">
                                    <p style={{ whiteSpace: 'pre-wrap' }}>{card.desc}</p>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    {rulings.length > 0 && (
                        <div className="mt-3">
                            <h4>Card Rulings & Interactions</h4>
                            <ul className="list-group">
                                {rulings.map((ruling, index) => (
                                    <li key={index} className="list-group-item">
                                        <i className="fas fa-gavel me-2 text-secondary"></i>
                                        {ruling}
                                    </li>
                                ))}
                            </ul>
                        </div>
                    )}
                </div>
                <div className="modal-footer">
                    <button type="button" className="btn btn-secondary" onClick={onClose}>Close</button>
                </div>
            </div>
        </div>
    );
};

ReactDOM.render(<App />, document.getElementById('deck-analyzer-app'));