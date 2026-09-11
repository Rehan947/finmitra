/**
 * FinMitra — Interactive Budget Calculator
 * Provides real-time calculation, visual allocation bar, edge-case safety, and practical insights.
 */

class BudgetCalculator {
  constructor() {
    this.incomeInput = document.getElementById("budget-income");
    this.essentialsInput = document.getElementById("budget-essentials");
    this.nonEssentialsInput = document.getElementById("budget-nonessentials");
    this.savingsInput = document.getElementById("budget-savings");
    this.resetBtn = document.getElementById("budget-reset-btn");

    this.statIncome = document.getElementById("stat-income");
    this.statExpenses = document.getElementById("stat-expenses");
    this.statSavings = document.getElementById("stat-savings");
    this.statBalance = document.getElementById("stat-balance");
    this.balanceCard = document.getElementById("stat-balance-card");

    this.barEssentials = document.getElementById("bar-essentials");
    this.barNonEssentials = document.getElementById("bar-nonessentials");
    this.barSavings = document.getElementById("bar-savings");
    this.barRemaining = document.getElementById("bar-remaining");

    this.legendEssentials = document.getElementById("legend-essentials-pct");
    this.legendNonEssentials = document.getElementById("legend-nonessentials-pct");
    this.legendSavings = document.getElementById("legend-savings-pct");
    this.legendRemaining = document.getElementById("legend-remaining-pct");

    this.insightsList = document.getElementById("budget-insights-list");

    this.init();
  }

  init() {
    if (!this.incomeInput) return;

    const inputs = [this.incomeInput, this.essentialsInput, this.nonEssentialsInput, this.savingsInput];
    inputs.forEach(input => {
      input.addEventListener("input", () => this.calculate());
    });

    if (this.resetBtn) {
      this.resetBtn.addEventListener("click", () => this.reset());
    }

    // Initial calculation with placeholder values
    this.calculate();
  }

  parseValue(input) {
    if (!input || !input.value) {
      if (input) input.classList.remove("input-warning");
      return 0;
    }
    const val = parseFloat(input.value);
    if (isNaN(val)) {
      input.classList.remove("input-warning");
      return 0;
    }
    if (val < 0) {
      input.classList.add("input-warning");
      return 0;
    }
    input.classList.remove("input-warning");
    return val;
  }

  formatCurrency(num) {
    return "₹" + Number(num).toLocaleString("en-IN", {
      minimumFractionDigits: 0,
      maximumFractionDigits: 2
    });
  }

  calculate() {
    const income = this.parseValue(this.incomeInput);
    const essentials = this.parseValue(this.essentialsInput);
    const nonEssentials = this.parseValue(this.nonEssentialsInput);
    const savings = this.parseValue(this.savingsInput);

    const totalExpenses = essentials + nonEssentials;
    const remainingBalance = income - totalExpenses - savings;

    // Update stat cards
    this.statIncome.textContent = this.formatCurrency(income);
    this.statExpenses.textContent = this.formatCurrency(totalExpenses);
    this.statSavings.textContent = this.formatCurrency(savings);
    this.statBalance.textContent = this.formatCurrency(remainingBalance);

    // Style balance card based on deficit or surplus
    if (remainingBalance < 0) {
      this.balanceCard.className = "stat-box highlight-deficit";
    } else {
      this.balanceCard.className = "stat-box highlight-balance";
    }

    // Calculate allocation ratios
    let essentialsPct = 0;
    let nonEssentialsPct = 0;
    let savingsPct = 0;
    let remainingPct = 0;

    if (income > 0) {
      essentialsPct = Math.min(100, (essentials / income) * 100);
      nonEssentialsPct = Math.min(100 - essentialsPct, (nonEssentials / income) * 100);
      savingsPct = Math.min(100 - essentialsPct - nonEssentialsPct, (savings / income) * 100);
      remainingPct = Math.max(0, 100 - essentialsPct - nonEssentialsPct - savingsPct);
    }

    // Update progress bar
    if (this.barEssentials) this.barEssentials.style.width = essentialsPct.toFixed(1) + "%";
    if (this.barNonEssentials) this.barNonEssentials.style.width = nonEssentialsPct.toFixed(1) + "%";
    if (this.barSavings) this.barSavings.style.width = savingsPct.toFixed(1) + "%";
    if (this.barRemaining) this.barRemaining.style.width = remainingPct.toFixed(1) + "%";

    // Update legend labels
    if (this.legendEssentials) this.legendEssentials.textContent = `(${essentialsPct.toFixed(0)}%)`;
    if (this.legendNonEssentials) this.legendNonEssentials.textContent = `(${nonEssentialsPct.toFixed(0)}%)`;
    if (this.legendSavings) this.legendSavings.textContent = `(${savingsPct.toFixed(0)}%)`;
    if (this.legendRemaining) this.legendRemaining.textContent = `(${remainingPct.toFixed(0)}%)`;

    // Generate practical educational insights
    this.generateInsights(income, essentials, nonEssentials, savings, remainingBalance);
  }

  generateInsights(income, essentials, nonEssentials, savings, balance) {
    if (!this.insightsList) return;
    this.insightsList.innerHTML = "";

    const insights = [];

    if (income === 0) {
      insights.push("Enter your estimated monthly earnings to see how your money is allocated.");
      insights.push("Tip: If income varies, use your average lowest monthly income for a safe baseline.");
    } else if (balance < 0) {
      const deficit = Math.abs(balance);
      insights.push(`Your planned expenses exceed income by ${this.formatCurrency(deficit)}. This can lead to debt.`);
      insights.push("Immediate step: Pause non-essential purchases for 14 days and prioritize food, rent, and utilities.");
      insights.push("Ask FinMitra: 'How do I cut non-essential expenses without feeling deprived?'");
    } else if (balance === 0) {
      insights.push("Zero-sum budget achieved: Every rupee has a dedicated job!");
      if (savings > 0) {
        insights.push(`Great job saving ${this.formatCurrency(savings)} monthly towards your financial safety net.`);
      } else {
        insights.push("Try redirecting even ₹200 to ₹500 from non-essentials into a starter emergency fund.");
      }
    } else {
      insights.push(`You have an unallocated buffer of ${this.formatCurrency(balance)} this month.`);
      if (savings < (income * 0.1)) {
        insights.push("Recommended: Channel some of this surplus into your emergency buffer before spending it.");
      } else {
        insights.push("Solid financial discipline! Keep building until you have 1–3 months of essential expenses stored safely.");
      }
    }

    insights.forEach(text => {
      const li = document.createElement("li");
      li.textContent = text;
      this.insightsList.appendChild(li);
    });
  }

  reset() {
    [this.incomeInput, this.essentialsInput, this.nonEssentialsInput, this.savingsInput].forEach(inp => {
      if (inp) {
        inp.value = "";
        inp.classList.remove("input-warning");
      }
    });
    this.calculate();
  }
}

document.addEventListener("DOMContentLoaded", () => {
  window.finmitraBudget = new BudgetCalculator();
});
