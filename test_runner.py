#!/usr/bin/env python
"""
Comprehensive test runner for all packages in the uv workspace.
Handles package dependencies and runs tests in the correct environment.
"""
import subprocess
import sys
import os
from pathlib import Path
from typing import List, Tuple

class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    YELLOW = '\033[93m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(text: str):
    """Print a formatted header"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'=' * 60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text:^60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 60}{Colors.END}\n")

def print_package_header(package: str):
    """Print a package test header"""
    print(f"\n{Colors.BOLD}📦 Testing {package}...{Colors.END}")
    print(f"{'-' * 40}")

def sync_package_deps(package_path: Path):
    """Sync package dependencies including test extras"""
    print(f"  Installing dependencies...")
    result = subprocess.run(
        ["uv", "sync", "--extra", "test"],
        cwd=package_path,
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        print(f"  {Colors.YELLOW}Warning: Could not sync test dependencies{Colors.END}")

def run_package_tests(package_path: Path) -> Tuple[bool, int, str]:
    """
    Run tests for a single package.
    Returns: (success, test_count, output)
    """
    # First sync dependencies
    sync_package_deps(package_path)
    
    # Run pytest
    result = subprocess.run(
        ["uv", "run", "pytest", "-v", "--tb=short"],
        cwd=package_path,
        capture_output=True,
        text=True
    )
    
    output = result.stdout + result.stderr
    success = result.returncode == 0
    
    # Parse test count from output
    test_count = 0
    for line in output.split('\n'):
        # Look for pytest summary line like "====== 12 passed in 0.04s ======"
        if "passed" in line and "=" in line:
            import re
            match = re.search(r'(\d+)\s+passed', line)
            if match:
                test_count = int(match.group(1))
                break
    
    return success, test_count, output

def main():
    """Main test runner"""
    packages = [
        "rag-core",
        "storm-client",
        "rag-engine", 
        "rag-service",
        "rag-api"
    ]
    
    print_header("Running Tests for All RAG Packages")
    
    # Track results
    total_passed = 0
    total_failed = 0
    failed_packages = []
    results = {}
    
    # Run tests for each package
    for package in packages:
        package_path = Path(f"packages/{package}")
        if not package_path.exists():
            print(f"{Colors.RED}❌ Package {package} not found!{Colors.END}")
            continue
            
        print_package_header(package)
        
        success, test_count, output = run_package_tests(package_path)
        
        if success:
            print(f"  {Colors.GREEN}✅ {test_count} tests passed{Colors.END}")
            total_passed += test_count
            results[package] = ('passed', test_count)
        else:
            print(f"  {Colors.RED}❌ Tests failed{Colors.END}")
            failed_packages.append(package)
            results[package] = ('failed', 0)
            
            # Show errors for failed tests
            print(f"\n{Colors.RED}Errors:{Colors.END}")
            error_lines = []
            capture = False
            for line in output.split('\n'):
                if "FAILED" in line or "ERROR" in line:
                    capture = True
                if capture and (line.strip() == "" or "=" in line):
                    capture = False
                if capture:
                    error_lines.append(line)
            
            for line in error_lines[:10]:  # Show first 10 error lines
                print(f"  {line}")
            if len(error_lines) > 10:
                print(f"  ... and {len(error_lines) - 10} more lines")
    
    # Print summary
    print_header("Test Summary")
    
    print(f"{Colors.BOLD}Results by package:{Colors.END}")
    for package, (status, count) in results.items():
        if status == 'passed':
            print(f"  {package:<20} {Colors.GREEN}✅ {count} tests passed{Colors.END}")
        else:
            print(f"  {package:<20} {Colors.RED}❌ Failed{Colors.END}")
    
    print(f"\n{Colors.BOLD}Total:{Colors.END}")
    print(f"  Tests passed: {Colors.GREEN}{total_passed}{Colors.END}")
    if failed_packages:
        print(f"  Failed packages: {Colors.RED}{', '.join(failed_packages)}{Colors.END}")
        return 1
    else:
        print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 All tests passed!{Colors.END}")
        return 0

if __name__ == "__main__":
    sys.exit(main())