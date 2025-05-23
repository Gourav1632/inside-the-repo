import { cn } from "@/lib/utils";

export const BentoGrid = ({
  className,
  children,
}: {
  className?: string;
  children?: React.ReactNode;
}) => {
  return (
    <div
      className={cn(
        " grid w-full grid-cols-1 h-[90vh]  gap-4   md:grid-cols-3",
        className,
      )}
    >
      {children}
    </div>
  );
};

export const BentoGridItem = ({
  className,
  title,
  description,
  header,
  icon,
}: {
  className?: string;
  title?: string | React.ReactNode;
  description?: any;
  header?: React.ReactNode;
  icon?: React.ReactNode;
}) => {
    if(title=="File Summary"){
        return (
          // bg-neutral-900 rounded-xl py-6 shadow-lg w-full h-full max-w-2xl border border-neutral-700 text-white
          <div
            className={cn(
              "group/bento  custom-scrollbar overflow-y-auto  row-span-1 flex flex-col justify-between space-y-4 rounded-xl border border-neutral-700 bg-[#121212] p-4 ",
              className,
            )}
          >
            {header}
            <div className="transition duration-200 group-hover/bento:translate-x-2">
              {icon}
              <div className="text-2xl font-semibold my-2 text-nowrap text-purple-400 ">
                {title}
              </div>
              <div className="font-sans  font-normal text-neutral-600 dark:text-neutral-300 break-words overflow-hidden">
                {description}
              </div>
            </div>
          </div>
        );
    }else if((title=="Functions" || title=="Classes")&& Array.isArray(description)){
        return (
          <div
            className={cn(
              "group/bento  custom-scrollbar overflow-y-auto  row-span-1 flex flex-col justify-between space-y-4 rounded-xl border border-neutral-700 bg-[#121212] p-4 ",
              className,
            )}
          >
            {header}
            <div className="transition duration-200 group-hover/bento:translate-x-2">
              {icon}
              <div className="text-2xl font-semibold my-2 text-nowrap text-purple-400 ">
                {title}
              </div>
              <div className="flex flex-col gap-2">

              {description?.length === 0 ? (
                  <div className="font-sans  font-normal text-neutral-600 dark:text-neutral-300">
                    No major {title.toLowerCase()}.
                </div>
                ) : (
                    description?.map((item, idx) => (
                        <div
                        key={idx}
                        className="font-sans font-normal text-neutral-600 dark:text-neutral-300 break-words overflow-hidden"
                        >
                    {item.name}
                    </div>
                ))
            )}
            </div>
            </div>
          </div>
        );
    }else if(title=="Imports" && Array.isArray(description)){
        return (
          <div
            className={cn(
              "group/bento  custom-scrollbar overflow-y-auto  row-span-1 flex flex-col justify-between space-y-4 rounded-xl border border-neutral-700 bg-[#121212] p-4 ",
              className,
            )}
          >
            {header}
            <div className="transition duration-200 group-hover/bento:translate-x-2">
              {icon}
              <div className="text-2xl font-semibold my-2 text-nowrap text-purple-400 ">
                {title}
              </div>
              <div className="flex flex-col gap-2">

              {
                  description?.map((item, idx)=>{
                      return (
                          <div key={idx} className="font-sans font-normal text-neutral-600 dark:text-neutral-300 break-words overflow-hidden">
                        {
                            item.content 
                        }
                    </div>
                    )
                })
            }
            </div>
            </div>
          </div>
        );
    }else if(title=="File Git History"){
        return (
          <div
            className={cn(
              "group/bento  custom-scrollbar overflow-y-auto  row-span-1 flex flex-col justify-between space-y-4 rounded-xl border border-neutral-700 bg-[#121212] p-4 ",
              className,
            )}
          >
            {header}
            <div className="transition duration-200 group-hover/bento:translate-x-2">
              {icon}
              <div className="text-2xl font-semibold my-2 text-nowrap text-purple-400 ">
                {title}
              </div>
              <div  className="font-sans font-normal text-neutral-600 dark:text-neutral-300 break-words overflow-hidden">
              <div>Commit Count : <span className="font-bold">{description.commit_count}</span></div>
              <div>Last modified : <span className="font-bold">{description.last_modified}</span></div>
              <div><span className="font-bold">Recents commits: </span></div>
              <div className="flex flex-col gap-2">
              {
                description.recent_commits.map((item,idx)=>{
                    return(
                        <div className="bg-neutral-900 p-4 rounded-xl shadow-lg w-full h-full border border-neutral-700 text-white overflow-hidden" key={idx}>
                            <div><span className="font-semibold">Author : </span>{item.author}</div>
                            <div><span className="font-semibold">Date : </span> {item.date}</div>
                            <div><span className="font-semibold">Message :</span> {item.message}</div>
                            <div><span className="font-semibold">Commit : </span>{item.sha}</div>
                        </div>
                    )
                })
              }
              </div>
            </div>
            </div>
          </div>
        );
    }else if(title== "Most "){

    }
};
