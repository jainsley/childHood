def convertScore(score):
    """Convert a numeric score between 0-100 to quintile categories."""
    if score == 'No data.'
        scoreValue = "No data."
    elif score <= 20:
        scoreValue = "Very Low"
    elif score > 20 and score <= 40:
        scoreValue = "Low"
    elif score > 40 and score <= 60:
        scoreValue = "Average"
    elif score > 60 and score <= 80:
        scoreValue = "High"
    elif score > 80:
        scoreValue = "Very High"
    return scoreValue

def valueColor(score, scoreType):
    """Associate a color to a category based on whether a lower value is better or a higher value is better."""
    goodColors = {"No data." : "#FFFFFF",
                  "Very Low" : "#FF0000",
                  "Low" : "#CC0000",
                  "Average" : "#FFFF00",
                  "High" : "#00CC00",
                  "Very High" : "#00FF00"}

    badColors = {"No data." : "#FFFFFF",
                 "Very Low" : "#00FF00",
                 "Low" : "#00CC00",
                 "Average" : "#FFFF00",
                 "High" : "#CC0000",
                 "Very High" : "#FF0000"}
    
    if scoreType == 'bad':
        return [convertScore(score), badColors[convertScore(score)]]
    elif scoreType == 'good':
        return [convertScore(score), goodColors[convertScore(score)]]