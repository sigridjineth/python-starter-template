#!/usr/bin/env python
"""Run tests for all packages in the workspace"""
import subprocess
import sys
import os

def run_tests():
    """Run tests for each package"""
    packages = [
        "rag-core",
        "storm-client", 
        "rag-engine",
        "rag-service",
        "rag-api"
    ]
    
    total_passed = 0
    total_failed = 0
    failed_packages = []
    
    print("=" * 60)
    print("Running tests for all packages")
    print("=" * 60)
    
    for package in packages:
        package_dir = f"packages/{package}"
        print(f"\n📦 Testing {package}...")
        print("-" * 40)
        
        # Run pytest from within each package directory
        result = subprocess.run(
            ["uv", "run", "pytest", "-v", "--tb=short"],
            cwd=package_dir,
            capture_output=True,
            text=True
        )
        
        # Parse output for test counts
        output = result.stdout + result.stderr
        
        if result.returncode == 0:
            # Look for test summary
            for line in output.split('\n'):
                if "passed" in line and "==" in line:
                    # Extract number of passed tests
                    parts = line.split()
                    for i, part in enumerate(parts):
                        if part == "passed":
                            try:
                                count = int(parts[i-1])
                                total_passed += count
                                print(f"✅ {count} tests passed")
                            except:
                                pass
                    break
        else:
            failed_packages.append(package)
            print(f"❌ Tests failed for {package}")
            # Print the actual error
            print(output)
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Total tests passed: {total_passed}")
    if failed_packages:
        print(f"Failed packages: {', '.join(failed_packages)}")
        return 1
    else:
        print("✅ All packages passed!")
        return 0

if __name__ == "__main__":
    sys.exit(run_tests())