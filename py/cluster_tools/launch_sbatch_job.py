import os
import base64
import argparse
import subprocess

SBATCH_TEMPLATE='''
#!/bin/bash
#SBATCH --nodes={nodes}
#SBATCH --ntasks={ntasks}
#SBATCH --cpus-per-task={cpus_per_task}
#SBATCH --time={hours}:{minutes}:{seconds}
#SBATCH --mem={memory}
#SBATCH --job-name={job_name}
#SBATCH --mail-type=END
#SBATCH --mail-user{mail_addr}
#SBATCH --output={job_output}
#SBATCH --error={job_error}
echo 'Processing...'
time {command}
echo 'Done!'
'''

def launch_job(command, nodes, ntasks, cpus_per_tasks, job_output, job_error, hours, minutes, seconds, memory, job_name, mail_addr):
    #create a randomized string in base64 with a .sbatch extension
    tempfilename = base64.b64encode(command, 'ab')[:10]+'.sbatch'
    #create/open a file with the write option, store its file handle, write to the file
    tempfile = open(tempfilename, 'w')
    tempfile.write(SBATCH_TEMPLATE.format(command=command, hours=hours))
    tempfile.close()

    #run the script by running qsub with the pbs file we just created
    sbatch_cmd = 'sbatch {jobscript}'.format(jobscript=tempfilename)
    #the subprocess module pauses the execution of the script and waits for the output from stdout
    output = subprocess.check_output(sbatch_cmd, shell=True)
    #delete the .pbs file we just made to keep stuff clean.
    os.remove(tempfilename)
    return command, output.strip()

if __name__ == '__main__':
    #create a parser for arguments, add some arguments, parse arguments stored in argv
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--command', required=True, help='command to be injected into .pbs file.')
    parser.add_argument('-nodes', '--nodes', default=1, help='the number of nodes your job will have')
    parser.add_argument('-ntasks', '--ntasks', default=1, help='the number of tasks, processes, or programs that will run on your node')
    parser.add_argument('-cpt', '--cpus-per-task', default=1, help='the number of cpus you want to allocate for each task/process/program')
    parser.add_argument('-o', '--joboutput', default='localhost:${{HOME}}/job_output_%%A_%%a.out', help='the output log path you would like to give your job, this is optional')
    parser.add_argument('-e', '--joberror', default='localhost:${{HOME}}/job_output_%%A_%%a.err', help='the error log path you would like to give your job, this is optional')
    parser.add_argument('-w', '--hours', default='01', help='the number of hours the job will take')
    parser.add_argument('-m', '--minutes', default='00', help='the number of minutes, optional')
    parser.add_argument('-s', '--seconds', default='00', help='the number of seconds to give to your job, optional')
    parser.add_argument('-me', '--memory', default='15GB', help='the amount of memory you need to give to your job, optional')
    parser.add_argument('-j', '--job-name', default='smapp_job', help='the name of your job, optional')
    parser.add_argument('-ma', '--mail-addr', default='${{LOGNAME}}@nyu.edu', help='the mail address to send job reports to, optional')
    args = parser.parse_args()

    #create an empty list
    command, job_number = launch_job(args.command, args.nodes, args.ntasks, args.cpus_per_task, args.joboutput, args.joberror, args.hours, args.minutes, args.seconds, args.memory, args.job_name, args.mail_addr)
    print('{jobnumber}: {command} (walltime: {hours})').format(jobnumber=job_number, command=command, hours=args.hours)

'''
author @yvan

this script takes inputs (many can be omitted and left at defaults) and launches an sbatch
job on the nyu hpc prince cluster.
'''