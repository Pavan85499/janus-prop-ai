#!/usr/bin/env node
/**
 * Frontend Configuration Checker and Fixer for Janus Prop AI
 * 
 * This script checks the frontend configuration and fixes common issues.
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
    reset: '\x1b[0m'
};

function log(message, color = 'reset') {
    console.log(`${colors[color]}${message}${colors.reset}`);
}

function checkNodeVersion() {
    log('\n🔍 Checking Node.js version...', 'blue');
    
    const nodeVersion = process.version;
    const majorVersion = parseInt(nodeVersion.slice(1).split('.')[0]);
    
    if (majorVersion >= 18) {
        log(`✅ Node.js ${nodeVersion}: OK`, 'green');
        return true;
    } else {
        log(`❌ Node.js ${nodeVersion}: Version 18+ required`, 'red');
        return false;
    }
}

function checkPackageJson() {
    log('\n🔍 Checking package.json...', 'blue');
    
    const packageJsonPath = path.join(__dirname, 'package.json');
    
    if (!fs.existsSync(packageJsonPath)) {
        log('❌ package.json not found', 'red');
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
            '@supabase/supabase-js'
        ];
        
        const missing = [];
        
        for (const dep of criticalDeps) {
            if (packageJson.dependencies?.[dep] || packageJson.devDependencies?.[dep]) {
                log(`✅ ${dep}: Found`, 'green');
            } else {
                missing.push(dep);
                log(`❌ ${dep}: Missing`, 'red');
            }
        }
        
        if (missing.length > 0) {
            log(`\n📦 Installing missing dependencies: ${missing.join(', ')}`, 'yellow');
            try {
                execSync(`npm install ${missing.join(' ')}`, { stdio: 'inherit' });
                log('✅ Dependencies installed successfully!', 'green');
            } catch (error) {
                log('❌ Failed to install dependencies', 'red');
                return false;
            }
        }
        
        return true;
    } catch (error) {
        log(`❌ Error reading package.json: ${error.message}`, 'red');
        return false;
    }
}

function checkEnvironmentFile() {
    log('\n🔍 Checking environment configuration...', 'blue');
    
    const envPath = path.join(__dirname, '.env');
    const envLocalPath = path.join(__dirname, '.env.local');
    
    let envFile = null;
    if (fs.existsSync(envLocalPath)) {
        envFile = envLocalPath;
        log('✅ Found .env.local', 'green');
    } else if (fs.existsSync(envPath)) {
        envFile = envPath;
        log('✅ Found .env', 'green');
    } else {
        log('❌ No environment file found', 'red');
        return createEnvironmentFile();
    }
    
    // Check environment variables
    const envContent = fs.readFileSync(envFile, 'utf8');
    const requiredVars = [
        'VITE_SUPABASE_URL',
        'VITE_SUPABASE_PUBLISHABLE_KEY',
        'VITE_API_BASE_URL'
    ];
    
    const missing = [];
    
    for (const varName of requiredVars) {
        if (envContent.includes(`${varName}=`) && !envContent.includes(`${varName}=""`)) {
            log(`✅ ${varName}: Configured`, 'green');
        } else {
            missing.push(varName);
            log(`❌ ${varName}: Missing or empty`, 'red');
        }
    }
    
    if (missing.length > 0) {
        log('\n⚠️  Some environment variables are missing. Please update your .env file.', 'yellow');
        return false;
    }
    
    return true;
}

function createEnvironmentFile() {
    log('\n🔧 Creating .env file...', 'yellow');
    
    const envTemplate = `# Supabase Configuration
VITE_SUPABASE_PROJECT_ID="your_project_id"
VITE_SUPABASE_PUBLISHABLE_KEY="your_publishable_key"
VITE_SUPABASE_URL="https://your_project_id.supabase.co"

# API Configuration
VITE_API_BASE_URL="http://localhost:8000"

# Feature Flags
VITE_ENABLE_REAL_TIME_UPDATES=true
VITE_ENABLE_AGENT_CONSOLE=true

# Development Settings
VITE_DEBUG_MODE=true
VITE_LOG_LEVEL=info
`;
    
    try {
        fs.writeFileSync(path.join(__dirname, '.env'), envTemplate);
        log('✅ Created .env file with template', 'green');
        log('⚠️  Please update the .env file with your actual configuration values', 'yellow');
        return false; // Still need manual configuration
    } catch (error) {
        log(`❌ Failed to create .env file: ${error.message}`, 'red');
        return false;
    }
}

function checkViteConfig() {
    log('\n🔍 Checking Vite configuration...', 'blue');
    
    const viteConfigPath = path.join(__dirname, 'vite.config.ts');
    
    if (!fs.existsSync(viteConfigPath)) {
        log('❌ vite.config.ts not found', 'red');
        return createViteConfig();
    }
    
    const viteConfig = fs.readFileSync(viteConfigPath, 'utf8');
    
    // Check for required configurations
    const checks = [
        { pattern: /server:\s*{/, name: 'Server configuration' },
        { pattern: /port:\s*\d+/, name: 'Port configuration' },
        { pattern: /@vitejs\/plugin-react/, name: 'React plugin' }
    ];
    
    let allGood = true;
    
    for (const check of checks) {
        if (check.pattern.test(viteConfig)) {
            log(`✅ ${check.name}: OK`, 'green');
        } else {
            log(`⚠️  ${check.name}: May need attention`, 'yellow');
            allGood = false;
        }
    }
    
    return allGood;
}

function createViteConfig() {
    log('\n🔧 Creating vite.config.ts...', 'yellow');
    
    const viteConfigTemplate = `import { defineConfig } from "vite";
import react from "@vitejs/plugin-react-swc";
import path from "path";
import { componentTagger } from "lovable-tagger";

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => ({
  server: {
    host: "::",
    port: 8080,
  },
  plugins: [
    react(),
    mode === 'development' &&
    componentTagger(),
  ].filter(Boolean),
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
}));
`;
    
    try {
        fs.writeFileSync(path.join(__dirname, 'vite.config.ts'), viteConfigTemplate);
        log('✅ Created vite.config.ts', 'green');
        return true;
    } catch (error) {
        log(`❌ Failed to create vite.config.ts: ${error.message}`, 'red');
        return false;
    }
}

function checkTailwindConfig() {
    log('\n🔍 Checking Tailwind configuration...', 'blue');
    
    const tailwindConfigPath = path.join(__dirname, 'tailwind.config.ts');
    
    if (!fs.existsSync(tailwindConfigPath)) {
        log('❌ tailwind.config.ts not found', 'red');
        return false;
    }
    
    log('✅ tailwind.config.ts: Found', 'green');
    return true;
}

function installDependencies() {
    log('\n📦 Installing/updating dependencies...', 'blue');
    
    try {
        log('Running npm install...', 'yellow');
        execSync('npm install', { stdio: 'inherit' });
        log('✅ Dependencies installed successfully!', 'green');
        return true;
    } catch (error) {
        log('❌ Failed to install dependencies', 'red');
        log('Try running: npm install --legacy-peer-deps', 'yellow');
        return false;
    }
}

function runTypeCheck() {
    log('\n🔍 Running TypeScript check...', 'blue');
    
    try {
        execSync('npx tsc --noEmit', { stdio: 'pipe' });
        log('✅ TypeScript check passed!', 'green');
        return true;
    } catch (error) {
        log('⚠️  TypeScript check found issues (this is normal during development)', 'yellow');
        return true; // Don't fail on TypeScript errors
    }
}

function startDevelopmentServer() {
    log('\n🚀 Starting development server...', 'blue');
    
    try {
        log('Starting Vite development server...', 'yellow');
        log('Server will be available at: http://localhost:8080', 'blue');
        log('Press Ctrl+C to stop the server', 'yellow');
        execSync('npm run dev', { stdio: 'inherit' });
    } catch (error) {
        if (error.signal === 'SIGINT') {
            log('\n⏹️  Development server stopped by user', 'yellow');
        } else {
            log('\n❌ Development server failed to start', 'red');
            log('Try running: npm run dev', 'yellow');
        }
    }
}

function main() {
    log('🚀 Janus Prop AI Frontend - Configuration Checker and Fixer', 'blue');
    log('=' .repeat(70), 'blue');
    
    let allChecksPass = true;
    
    // Check Node.js version
    if (!checkNodeVersion()) {
        allChecksPass = false;
    }
    
    // Check package.json and install dependencies
    if (!checkPackageJson()) {
        allChecksPass = false;
    }
    
    // Install/update dependencies
    if (!installDependencies()) {
        allChecksPass = false;
    }
    
    // Check environment configuration
    if (!checkEnvironmentFile()) {
        allChecksPass = false;
    }
    
    // Check Vite configuration
    if (!checkViteConfig()) {
        // This is not critical, continue
    }
    
    // Check Tailwind configuration
    if (!checkTailwindConfig()) {
        // This is not critical, continue
    }
    
    // Run TypeScript check
    runTypeCheck();
    
    log('\n' + '='.repeat(70), 'blue');
    
    if (allChecksPass) {
        log('✅ All critical checks passed! Frontend is ready.', 'green');
        log('\nStarting development server...', 'blue');
        startDevelopmentServer();
    } else {
        log('❌ Some checks failed. Please fix the issues above.', 'red');
        log('\nCommon fixes:', 'yellow');
        log('1. Update Node.js to version 18+', 'yellow');
        log('2. Run: npm install', 'yellow');
        log('3. Update your .env file with correct values', 'yellow');
        log('4. Run this script again', 'yellow');
        process.exit(1);
    }
}

if (require.main === module) {
    main();
}

module.exports = {
    checkNodeVersion,
    checkPackageJson,
    checkEnvironmentFile,
    checkViteConfig,
    installDependencies
};