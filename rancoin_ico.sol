//Rancoin ICO

//Version of compiler
pragma solidity ^0.5.3;

contract rancoin_ico {
    
    //Total number of Rancoin available for sale
    uint public max_rancoins = 100000;
    
    //INR to Rancoin conversion rate 
    uint public inr_to_rancoins = 100; 
    
    //Total number of Rancoin bought by investors
    uint public total_rancoins_bought = 0;
    
    //Mapping from investor address to its equity in Rancoins and INR 
    mapping(address => uint) equity_rancoins;
    mapping(address => uint) equity_inr;
    
    //Checking if an investor can buy Rancoins
    modifier can_buy_rancoins(uint inr_invested) {
        
        require (inr_invested * inr_to_rancoins + total_rancoins_bought <= max_rancoins);
        _;
        
    }
    
    //Function to return the equity in Rancoins of an investor
    function equity_in_rancoins(address investor) external constant returns(uint) {
        
        return equity_rancoins[investor];
    }
    
    //Function to return the equity in INR of an investor
    function equity_in_inr(address investor) external constant returns(uint) {
        
        return equity_inr[investor];
    }
    
    //Function to buy rancoins
    function buy_rancoins(address investor, uint inr_invested) external 
    can_buy_rancoins(inr_invested) {

        uint rancoins_bought = inr_invested * inr_to_rancoins;

        equity_rancoins[investor] += rancoins_bought;
        equity_inr[investor] = equity_rancoins[investor] / inr_to_rancoins;
        total_rancoins_bought += rancoins_bought; 
    }

    //Function to sell rancoins
    function sell_rancoins(address investor, uint rancoins_sold) external {

        equity_rancoins[investor] -= rancoins_sold;
        equity_inr[investor] = equity_rancoins[investor] / inr_to_rancoins;
        total_rancoins_bought -= rancoins_sold; 
    }
}