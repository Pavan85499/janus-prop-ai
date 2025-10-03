#!/usr/bin/env node
/**
 * Frontend validation script for Janus Prop AI
 * 
 * This script validates the frontend setup and configuration.
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

// Colors for console output
const colors = {
    red: '\x1b[31m',
    green: '\x1b[32m',
    yellow: '\x1b[33m',
    blue: '\x1b[34m',
    magenta: '\x1b[95m',
    cyan: '\x1b[96m',
    reset: '\x1b[0m',
    bold: '\x1b[1m'
};

function log(message, color = 'reset', bold = false) {
    const prefix = bold ? colors.bold : '';
    console.log(`${prefix}${colors[color]}${message}${colors.reset}`);
}

function header(message) {
    log('='.repeat(60), 'cyan', true);
    log(` ${message} `, 'cyan', true);
    log('='.repeat(60), 'cyan', true);
}

function section(message) {
    log(`\n🔍 ${message}`, 'blue', true);
    log('-'.repeat(50), 'blue');
}

function success(message) {
    log(`✅ ${message}`, 'green');
}

function warning(message) {
    log(`⚠️  ${message}`, 'yellow');
}

function error(message) {
    log(`❌ ${message}`, 'red');
}

function info(message) {
    log(`ℹ️  ${message}`, 'blue');
}

function checkNodeVersion() {
    section('Checking Node.js Version');
    
    try {
        const version = process.version;
        const majorVersion = parseInt(version.slice(1).split('.')[0]);
        
        if (majorVersion >= 18) {
            success(`Node.js ${version}: Compatible`);
            return true;
        } else {
            error(`Node.js ${version}: Requires Node.js 18+`);
            return false;
        }
    } catch (e) {
        error(`Failed to check Node.js version: ${e.message}`);
        return false;
    }
}

function checkPackageJson() {
    section('Checking package.json');
    
    const packageJsonPath = path.join(__dirname, 'package.json');
    
    if (!fs.existsSync(packageJsonPath)) {
        error('package.json not found');
        return false;
    }
    
    try {
        const packageJson = JSON.parse(fs.readFileSync(packageJsonPath, 'utf8'));
        
        // Check critical dependencies
        const criticalDeps = [
            'react',
            'react-dom',
            'vite',
            'typescript',
            '@tanstack/react-query',
            '@supabase/supabase-js',
            'tailwindcss',
            'lucide-react'
        ];
        
        let allFound = true;
        
        for (const dep of criticalDeps) {
            if (packageJson.dependencies?.[dep] || packageJson.devDependencies?.[dep]) {
                success(`${dep}: Found`);
            } else {
                error(`${dep}: Missing`);
                allFound = false;
            }
        }
        
        if (allFound) {
            success('All critical dependencies found');
        }
        
        return allFound;
        
    } catch (e) {
        error(`Failed to read package.json: ${e.message}`);
        return false;
    }
}

function checkEnvironmentFile() {
    section('Checking Environment Configuration');
    
    const envPath = path.join(__dirname, '.env');
    const envLocalPath = path.join(__dirname, '.env.local');
    
    let envFile = null;
    if (fs.existsSync(envLocalPath)) {
        envFile = envLocalPath;
        success('Found .env.local');
    } else if (fs.existsSync(envPath)) {
        envFile = envPath;
        success('Found .env');
    } else {
        error('No environment file found (.env or .env.local)');
        return false;
    }
    
    try {
        const envContent = fs.readFileSync(envFile, 'utf8');
        
        // Check required variables
        const requiredVars = [
            'VITE_SUPABASE_URL',
            'VITE_SUPABASE_PUBLISHABLE_KEY',
            'VITE_API_BASE_URL'
        ];
        
        let allConfigured = true;
        
        for (const varName of requiredVars) {
            if (envContent.includes(`${varName}=`) && !envContent.includes(`${varName}=\""`)) {
                success(`${varName}: Configured`);
            } else {
                error(`${varName}: Missing or empty`);
                allConfigured = false;
            }
        }
        
        // Check optional variables
        const optionalVars = [
            'VITE_ENABLE_REAL_TIME_UPDATES',
            'VITE_ENABLE_AGENT_CONSOLE',
            'VITE_DEBUG_MODE'
        ];
        
        for (const varName of optionalVars) {
            if (envContent.includes(`${varName}=`)) {
                success(`${varName}: Configured`);
            } else {
                warning(`${varName}: Not set (using defaults)`);
            }
        }
        
        return allConfigured;
        
    } catch (e) {
        error(`Failed to read environment file: ${e.message}`);
        return false;
    }
}

function checkConfigFiles() {
    section('Checking Configuration Files');
    
    const configFiles = [
        'vite.config.ts',
        'tailwind.config.ts',
        'tsconfig.json',
        'postcss.config.js'
    ];
    
    let allFound = true;
    
    for (const file of configFiles) {
        const filePath = path.join(__dirname, file);
        if (fs.existsSync(filePath)) {
            success(`${file}: Found`);
        } else {
            warning(`${file}: Missing (may be optional)`);
            if (file === 'vite.config.ts' || file === 'tsconfig.json') {
                allFound = false;
            }
        }
    }
    
    return allFound;
}

function checkSourceStructure() {
    section('Checking Source Structure');
    
    const requiredDirs = [
        'src',
        'src/components',
        'src/pages',
        'src/lib',
        'src/hooks'
    ];
    
    const requiredFiles = [
        'src/App.tsx',
        'src/main.tsx',
        'src/index.css'
    ];
    
    let allFound = true;

    // Check directories
    for (const dir of requiredDirs) {
        const dirPath = path.join(__dirname, dir);
        if (fs.existsSync(dirPath) && fs.statSync(dirPath).isDirectory()) {
            success(`${dir}/: Found`);
        } else {
            error(`${dir}/: Missing`);
            allFound = false;
        }
    }

    // Check files
    for (const file of requiredFiles) {
        const filePath = path.join(__dirname, file);
        if (fs.existsSync(filePath)) {
            success(`${file}: Found`);
        } else {
            error(`${file}: Missing`);
            allFound = false;
        }
    }
    
    return allFound;
}

function main() {
    header('🚀 Janus Prop AI Frontend - Validation');

    const tests = [
        { name: 'Node.js Version', fn: checkNodeVersion, critical: true },
        { name: 'Package.json', fn: checkPackageJson, critical: true },
        { name: 'Environment Config', fn: checkEnvironmentFile, critical: true },
        { name: 'Config Files', fn: checkConfigFiles, critical: true },
        { name: 'Source Structure', fn: checkSourceStructure, critical: true },
    ];

    let passed = 0;
    let criticalPassed = 0;
    let totalCritical = 0;

    for (const test of tests) {
        try {
            const result = test.fn();
            if (result) {
                passed++;
                if (test.critical) {
                    criticalPassed++;
                }
            }
        } catch (e) {
            error(`${test.name} failed with error: ${e.message}`);
        }
        if (test.critical) {
            totalCritical++;
        }
    }

    log('\n' + '='.repeat(60), 'cyan', true);
    log('📊 Validation Results', 'cyan', true);
    log(`🔥 Critical Tests: ${criticalPassed}/${totalCritical} passed`, 'blue', true);

    if (criticalPassed === totalCritical) {
        success('🎉 All critical tests passed! Frontend is ready.');
        info('\nYou can now start the frontend with:');
        info('  npm run dev');
    } else {
        error('❌ Some critical tests failed. Please fix the issues above.');
        info('\n  Common fixes:');
        info('  - Run `npm install`');
        info('  - Update your .env file with correct values');
        info('  - Check Node.js version (requires 18+)');
        info('  - Run this script again after fixes.');
    }
}

if (require.main === module) {
    main();
}
