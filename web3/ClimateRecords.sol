// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract ClimateRecords {
    struct Record {
        string country;
        uint256 year;
        uint256 happinessScore; // multiplied by 100 to avoid decimals
        uint256 co2PerCapita;   // multiplied by 100
        address recorder;
    }

    Record[] public records;

    event RecordAdded(
        string country, 
        uint256 year, 
        uint256 happinessScore, 
        uint256 co2PerCapita, 
        address recorder
    );

    function addRecord(
        string memory _country, 
        uint256 _year, 
        uint256 _happinessScore, 
        uint256 _co2PerCapita
    ) public {
        records.push(Record({
            country: _country,
            year: _year,
            happinessScore: _happinessScore,
            co2PerCapita: _co2PerCapita,
            recorder: msg.sender
        }));
        
        emit RecordAdded(_country, _year, _happinessScore, _co2PerCapita, msg.sender);
    }

    function getTotalRecords() public view returns (uint256) {
        return records.length;
    }
}
