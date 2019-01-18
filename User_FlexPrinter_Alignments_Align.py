from Core import Procedure
import Procedures.User_FlexPrinter_Alignments_Update
import Procedures.User_FlexPrinter_Alignments_Derive
import json
import time


class User_FlexPrinter_Alignments_Align(Procedure):
    def Prepare(self):
        self.name = 'User_FlexPrinter_Alignments_Align'
        self.requirements['Measured_List']={'source':'apparatus', 'address':['information','alignmentnames'], 'value':'', 'desc':'parameters used to generate toolpath'}
        self.requirements['primenoz']={'source':'apparatus', 'address':'', 'value':'', 'desc':'prime material'}
        self.requirements['filename']={'source':'apparatus', 'address':'', 'value':'', 'desc':'name of alignmentfile'}
        self.requirements['filename']['address']=['information','alignmentsfile']
        self.updatealign = Procedures.User_FlexPrinter_Alignments_Update(self.apparatus, self.executor)
        self.derivealign = Procedures.User_FlexPrinter_Alignments_Derive(self.apparatus, self.executor)
    
    def Plan(self):
        measuredlist = self.requirements['Measured_List']['value']
        primenoz = self.requirements['primenoz']['value']
        filename = self.requirements['filename']['value']
        
        # Doing stuff
        
        # Check for loading file
        alignmentscollected = False
        doalignment = input('Import alignments from file?([y]/n/filename)')
        if doalignment in ['y', 'Y', 'yes', 'Yes', 'YES', '']:
            afilename = input('What filename?([' + filename + '])')
            if afilename == '':
                afilename = filename
            try:
                with open(filename, 'r') as TPjson:
                    self.apparatus['information']['alignments'] = json.load(TPjson)
                alignmentscollected = True
            except FileNotFoundError:
                print('No file loaded.  Possible error in ' + afilename)
        
        # If alignments were not collected from a file, collect them directly
        if not alignmentscollected:
            for alignment in measuredlist:
                self.updatealign.Do({'alignmentname':alignment})
        
        # Check if any alignments need to be redone
        alignmentsOK = False
        while not alignmentsOK:
            redoalignments = input('Would you like to redo any alignments?(y/[n])')
            if redoalignments in ['y', 'Y', 'yes', 'Yes', 'YES']:
                namestring = ''
                for name in measuredlist:
                    namestring += name + ' '
                which_alignment = input('Which alignment would you like to redo? (pick from list below)\n'+namestring)
                if which_alignment in measuredlist:
                    self.updatealign.Do({'alignmentname': which_alignment})
                else:
                    print('Alignment is not in list.')
            else:
                alignmentsOK = True

        # Use the measured alignments to derive the remaining needed alignments
        self.derivealign.Do({'Measured_List': measuredlist, 'primenoz': primenoz})

        # Save a copy of the alignments to the main folder and to the log folder
        with open(filename, 'w') as TPjson:
            json.dump(self.apparatus['information']['alignments'], TPjson)

        with open('Logs/'+str(int(round(time.time(), 0)))+filename, 'w') as TPjson:
            json.dump(self.apparatus['information']['alignments'], TPjson)
 
    def PrintAlignments(self, alignments):
        printstr = ''
        alignlist = list(alignments.keys())
        for alignment in alignlist:
            printstr = printstr + alignment + '\n'+ ' '
            dimlist = list(alignments[alignment].keys())
            for dim in dimlist:
                printstr += dim + ' ' + str(alignments[alignment][dim])
            printstr += '\n\n'
        print(printstr)
        


