#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

// Pages that should have the sidebar
const pagesWithSidebar = [
  'Agents.tsx',
  'Analytics.tsx', 
  'Automation.tsx',
  'BackendTest.tsx',
  'DealRoom.tsx',
  'DocumentManagement.tsx',
  'ExecutionClosing.tsx',
  'LegalCompliance.tsx',
  'Portfolios.tsx',
  'PostAcquisition.tsx',
  'Properties.tsx',
  'PropertyScanner.tsx',
  'Settings.tsx',
  'SubscriptionManagement.tsx',
  'Underwriting.tsx',
  'AIInvestmentCommittee.tsx'
];

// Pages that should NOT have the sidebar
const pagesWithoutSidebar = [
  'Landing.tsx',
  'Login.tsx', 
  'Signup.tsx',
  'NotFound.tsx',
  'ScheduleDemo.tsx' // This one has its own layout
];

const pagesDir = path.join(__dirname, '../src/pages');

function addSidebarToPage(filename) {
  const filePath = path.join(pagesDir, filename);
  
  if (!fs.existsSync(filePath)) {
    console.log(`❌ File not found: ${filename}`);
    return;
  }

  let content = fs.readFileSync(filePath, 'utf8');
  
  // Check if already has AppLayout
  if (content.includes('AppLayout')) {
    console.log(`✅ ${filename} already has AppLayout`);
    return;
  }

  // Add AppLayout import
  if (!content.includes('import { AppLayout }')) {
    // Find the last import statement
    const importRegex = /^import.*from.*['"];?\s*$/gm;
    const imports = content.match(importRegex);
    
    if (imports) {
      const lastImport = imports[imports.length - 1];
      const lastImportIndex = content.lastIndexOf(lastImport);
      const insertIndex = lastImportIndex + lastImport.length;
      
      content = content.slice(0, insertIndex) + 
        '\nimport { AppLayout } from "@/components/layout/AppLayout";' +
        content.slice(insertIndex);
    }
  }

  // Wrap the return statement with AppLayout
  // Look for return statement that starts with <div
  const returnRegex = /return\s*\(\s*<div/g;
  const match = content.match(returnRegex);
  
  if (match) {
    const returnIndex = content.indexOf(match[0]);
    const divIndex = content.indexOf('<div', returnIndex);
    
    // Insert AppLayout opening tag
    content = content.slice(0, divIndex) + 
      '<AppLayout>\n      ' + 
      content.slice(divIndex);
    
    // Find the closing </div> and add AppLayout closing tag
    // Count opening and closing divs to find the right closing tag
    let divCount = 0;
    let i = divIndex;
    let closingDivIndex = -1;
    
    while (i < content.length) {
      if (content.slice(i, i + 4) === '<div') {
        divCount++;
      } else if (content.slice(i, i + 6) === '</div>') {
        divCount--;
        if (divCount === 0) {
          closingDivIndex = i;
          break;
        }
      }
      i++;
    }
    
    if (closingDivIndex !== -1) {
      content = content.slice(0, closingDivIndex + 6) + 
        '\n    </AppLayout>' +
        content.slice(closingDivIndex + 6);
    }
  }

  // Write the updated content
  fs.writeFileSync(filePath, content);
  console.log(`✅ Added sidebar to ${filename}`);
}

function main() {
  console.log('🚀 Adding sidebar to all pages...\n');
  
  // Process pages that should have sidebar
  pagesWithSidebar.forEach(filename => {
    addSidebarToPage(filename);
  });
  
  console.log('\n📋 Summary:');
  console.log(`✅ Pages with sidebar: ${pagesWithSidebar.length}`);
  console.log(`🚫 Pages without sidebar: ${pagesWithoutSidebar.length}`);
  console.log('\n✨ Sidebar integration complete!');
}

main();
