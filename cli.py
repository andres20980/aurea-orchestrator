#!/usr/bin/env python
"""
Command-line interface for Aurea Orchestrator
"""

import argparse
import json
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.versions import get_agent_version, get_all_agent_versions, compare_versions
from job_metadata import JobMetadataStore


def cmd_agents_versions(args):
    """Show all agent versions"""
    versions = get_all_agent_versions()
    if args.json:
        print(json.dumps(versions, indent=2))
    else:
        print("Agent Versions:")
        for agent, version in sorted(versions.items()):
            print(f"  {agent}: {version}")


def cmd_agent_version(args):
    """Show specific agent version"""
    try:
        version = get_agent_version(args.agent)
        if args.json:
            print(json.dumps({args.agent: version}))
        else:
            print(f"{args.agent}: {version}")
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_compare_versions(args):
    """Compare two semantic versions"""
    result = compare_versions(args.version1, args.version2)
    
    if args.json:
        comparison = {
            'version1': args.version1,
            'version2': args.version2,
            'result': result,
            'description': 'equal' if result == 0 else ('less than' if result == -1 else 'greater than')
        }
        print(json.dumps(comparison, indent=2))
    else:
        if result == 0:
            print(f"{args.version1} == {args.version2}")
        elif result == -1:
            print(f"{args.version1} < {args.version2}")
        else:
            print(f"{args.version1} > {args.version2}")


def cmd_list_jobs(args):
    """List all jobs"""
    store = JobMetadataStore(args.storage_dir)
    jobs = store.list_jobs()
    
    if args.json:
        print(json.dumps({'jobs': jobs}, indent=2))
    else:
        if jobs:
            print(f"Jobs ({len(jobs)}):")
            for job_id in sorted(jobs):
                print(f"  {job_id}")
        else:
            print("No jobs found.")


def cmd_job_info(args):
    """Show job information"""
    store = JobMetadataStore(args.storage_dir)
    metadata = store.load(args.job_id)
    
    if metadata is None:
        print(f"Error: Job '{args.job_id}' not found", file=sys.stderr)
        sys.exit(1)
    
    if args.json:
        print(metadata.to_json())
    else:
        print(f"Job ID: {metadata.job_id}")
        print(f"Type: {metadata.job_type}")
        print(f"Status: {metadata.status}")
        print(f"Created: {metadata.created_at}")
        if hasattr(metadata, 'updated_at'):
            print(f"Updated: {metadata.updated_at}")
        print(f"Agent Versions:")
        for agent, version in sorted(metadata.agent_versions.items()):
            print(f"  {agent}: {version}")


def cmd_compare_jobs(args):
    """Compare two job runs"""
    store = JobMetadataStore(args.storage_dir)
    comparison = store.compare_runs(args.job1, args.job2)
    
    if args.json:
        print(json.dumps(comparison, indent=2))
    else:
        if 'error' in comparison:
            print(f"Error: {comparison['error']}", file=sys.stderr)
            sys.exit(1)
        
        print(f"Comparing Job {args.job1} vs Job {args.job2}")
        print("\nAgent Version Differences:")
        for agent, info in sorted(comparison['differences'].items()):
            if info['changed']:
                print(f"  {agent}: {info['job1_version']} -> {info['job2_version']}")
            else:
                print(f"  {agent}: {info['version']} (unchanged)")


def main():
    parser = argparse.ArgumentParser(
        description='Aurea Orchestrator CLI',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('--json', action='store_true', help='Output in JSON format')
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # agents versions command
    parser_agents_versions = subparsers.add_parser(
        'agents-versions',
        help='Show all agent versions'
    )
    parser_agents_versions.set_defaults(func=cmd_agents_versions)
    
    # agent version command
    parser_agent_version = subparsers.add_parser(
        'agent-version',
        help='Show specific agent version'
    )
    parser_agent_version.add_argument('agent', help='Agent name')
    parser_agent_version.set_defaults(func=cmd_agent_version)
    
    # compare versions command
    parser_compare_versions = subparsers.add_parser(
        'compare-versions',
        help='Compare two semantic versions'
    )
    parser_compare_versions.add_argument('version1', help='First version')
    parser_compare_versions.add_argument('version2', help='Second version')
    parser_compare_versions.set_defaults(func=cmd_compare_versions)
    
    # list jobs command
    parser_list_jobs = subparsers.add_parser(
        'list-jobs',
        help='List all jobs'
    )
    parser_list_jobs.add_argument('--storage-dir', default='.aurea/jobs', help='Job storage directory')
    parser_list_jobs.set_defaults(func=cmd_list_jobs)
    
    # job info command
    parser_job_info = subparsers.add_parser(
        'job-info',
        help='Show job information'
    )
    parser_job_info.add_argument('job_id', help='Job ID')
    parser_job_info.add_argument('--storage-dir', default='.aurea/jobs', help='Job storage directory')
    parser_job_info.set_defaults(func=cmd_job_info)
    
    # compare jobs command
    parser_compare_jobs = subparsers.add_parser(
        'compare-jobs',
        help='Compare two job runs'
    )
    parser_compare_jobs.add_argument('job1', help='First job ID')
    parser_compare_jobs.add_argument('job2', help='Second job ID')
    parser_compare_jobs.add_argument('--storage-dir', default='.aurea/jobs', help='Job storage directory')
    parser_compare_jobs.set_defaults(func=cmd_compare_jobs)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    args.func(args)


if __name__ == '__main__':
    main()
