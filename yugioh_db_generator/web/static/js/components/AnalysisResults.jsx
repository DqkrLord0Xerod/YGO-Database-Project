// yugioh_db_generator/web/static/js/components/AnalysisResults.jsx
const AnalysisResults = ({ analysis }) => {
    // Ensure the analysis object exists
    if (!analysis) {
        return <div className="alert alert-warning">No analysis data available.</div>;
    }

    return (
        <div>
            <h2 className="mb-4">Deck Analysis Results</h2>
            
            {/* Scores Section */}
            <div className="row mb-4">
                <div className="col-md-3">
                    <div className="score-card">
                        <h4>Overall Score</h4>
                        <div className="score-value text-primary">{analysis.overall_score}/100</div>
                    </div>
                </div>
                <div className="col-md-3">
                    <div className="score-card">
                        <h4>Consistency</h4>
                        <div className="score-value text-success">{analysis.consistency_score}/100</div>
                    </div>
                </div>
                <div className="col-md-3">
                    <div className="score-card">
                        <h4>Power</h4>
                        <div className="score-value text-danger">{analysis.power_score}/100</div>
                    </div>
                </div>
                <div className="col-md-3">
                    <div className="score-card">
                        <h4>Resilience</h4>
                        <div className="score-value text-info">{analysis.resilience_score}/100</div>
                    </div>
                </div>
            </div>
            
            {/* Card Types Section */}
            <h3 className="mb-3">Card Composition</h3>
            <div className="row mb-4">
                {Object.entries(analysis.card_types || {}).map(([type, count]) => (
                    count > 0 && (
                        <div key={type} className="col-md-2 mb-3">
                            <div className="stat-card">
                                <div className="stat-icon">
                                    {type.includes('monster') ? '👹' : 
                                    type.includes('spell') ? '📜' : 
                                    type.includes('trap') ? '⚡' : '🎴'}
                                </div>
                                <div>
                                    <div className="text-muted">{type.replace('_', ' ').toUpperCase()}</div>
                                    <div className="fs-4 fw-bold">{count}</div>
                                </div>
                            </div>
                        </div>
                    )
                ))}
            </div>
            
            {/* Archetypes Section */}
            {analysis.archetypes && Object.keys(analysis.archetypes).length > 0 && (
                <>
                    <h3 className="mb-3">Archetypes</h3>
                    <div className="row mb-4">
                        {Object.entries(analysis.archetypes).map(([archetype, count]) => (
                            <div key={archetype} className="col-md-3 mb-3">
                                <div className="stat-card">
                                    <div className="stat-icon">🏆</div>
                                    <div>
                                        <div className="text-muted">{archetype}</div>
                                        <div className="fs-4 fw-bold">{count} cards</div>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                </>
            )}
            
            {/* Strengths & Weaknesses */}
            <div className="row mb-4">
                <div className="col-md-6">
                    <div className="card">
                        <div className="card-header bg-success text-white">
                            <h4 className="mb-0">Strengths</h4>
                        </div>
                        <div className="card-body">
                            <ul className="list-group list-group-flush">
                                {analysis.strengths && analysis.strengths.map((strength, index) => (
                                    <li key={index} className="list-group-item">
                                        <i className="fas fa-check-circle text-success me-2"></i>
                                        {strength}
                                    </li>
                                ))}
                            </ul>
                        </div>
                    </div>
                </div>
                <div className="col-md-6">
                    <div className="card">
                        <div className="card-header bg-danger text-white">
                            <h4 className="mb-0">Weaknesses</h4>
                        </div>
                        <div className="card-body">
                            <ul className="list-group list-group-flush">
                                {analysis.weaknesses && analysis.weaknesses.map((weakness, index) => (
                                    <li key={index} className="list-group-item">
                                        <i className="fas fa-exclamation-circle text-danger me-2"></i>
                                        {weakness}
                                    </li>
                                ))}
                            </ul>
                        </div>
                    </div>
                </div>
            </div>
            
            {/* Recommendations */}
            <div className="card mb-4">
                <div className="card-header bg-primary text-white">
                    <h4 className="mb-0">Recommendations</h4>
                </div>
                <div className="card-body">
                    <ul className="list-group list-group-flush">
                        {analysis.recommendations && analysis.recommendations.map((recommendation, index) => (
                            <li key={index} className="list-group-item">
                                <i className="fas fa-lightbulb text-warning me-2"></i>
                                {recommendation}
                            </li>
                        ))}
                    </ul>
                </div>
            </div>
            
            {/* Meta Comparison (if available) */}
            {analysis.meta_comparison && Object.keys(analysis.meta_comparison).length > 0 && (
                <div className="card">
                    <div className="card-header bg-info text-white">
                        <h4 className="mb-0">Meta Comparison</h4>
                    </div>
                    <div className="card-body">
                        <ul className="list-group list-group-flush">
                            {Object.entries(analysis.meta_comparison).map(([key, value], index) => (
                                <li key={index} className="list-group-item">
                                    <strong>{key}:</strong> {value}
                                </li>
                            ))}
                        </ul>
                    </div>
                </div>
            )}
        </div>
    );
};